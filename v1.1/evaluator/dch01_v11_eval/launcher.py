"""Start one agent process per task and talk to it over the step API.

Step API, one JSON object per line:
  evaluator -> agent  {"type":"task","view":{...}}
  agent -> evaluator  {"type":"action","action":{...}}
  evaluator -> agent  {"type":"feedback","feedback":{...}}   (repeated until the task ends)
  evaluator -> agent  {"type":"end"}
The agent never receives anything else: no file paths, no seed, no gold.

Two isolation levels (see DECISIONS.md, D1):
  ProcessLauncher      Option 1. Separate process, empty working folder, cleared
                       environment, same OS user. Stops accidents, not a cheating agent.
  UserNetnsLauncher    Option 2. Linux only, started as root. The agent runs as the
                       unprivileged account dch-agent, in fresh network, process and
                       mount namespaces: no network, no view of other processes, and a
                       private empty /tmp that vanishes when the task ends.
"""
from __future__ import annotations
import json,os,pwd,resource,select,shutil,subprocess,sys,tempfile,time
from pathlib import Path

MAX_LINE=256*1024      # an action is tiny; a huge line is a fault, not an action
STDERR_KEEP=8*1024
AGENT_ENV={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','HOME':'/nonexistent'}


class AgentProtocolError(RuntimeError):
    pass


def _limits():
    # Runs in the child just before exec. Bounds CPU, memory and process count
    # so one task cannot stall the run or fork without limit.
    resource.setrlimit(resource.RLIMIT_CPU,(60,60))
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    resource.setrlimit(resource.RLIMIT_NPROC,(256,256))


class AgentSession:
    def __init__(self,argv,cwd,timeout,stderr_path):
        self.timeout=timeout;self.buf=b'';self.stderr_path=stderr_path
        # 0600: even through /proc/self/fd/2 the agent account cannot reopen this file for reading.
        self._err=os.fdopen(os.open(stderr_path,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600),'wb')
        self.proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self._err,
                                   cwd=cwd,env=dict(AGENT_ENV),close_fds=True,preexec_fn=_limits)

    def send(self,msg):
        try:
            # Key order is kept, not sorted: the v1.0 scripted readers take the first key of a
            # policy mapping, so sorting keys would change their FRA answers (see V11_VERIFICATION_REPORT.md).
            self.proc.stdin.write((json.dumps(msg)+'\n').encode());self.proc.stdin.flush()
        except (BrokenPipeError,OSError) as exc:raise AgentProtocolError('agent closed its input') from exc

    def receive(self):
        deadline=time.monotonic()+self.timeout
        fd=self.proc.stdout.fileno()
        while b'\n' not in self.buf:
            left=deadline-time.monotonic()
            if left<=0:raise AgentProtocolError('agent timeout')
            ready,_,_=select.select([fd],[],[],left)
            if not ready:continue
            chunk=os.read(fd,65536)
            if not chunk:raise AgentProtocolError('agent exited without an action')
            self.buf+=chunk
            if len(self.buf)>MAX_LINE:raise AgentProtocolError('agent line too long')
        line,self.buf=self.buf.split(b'\n',1)
        try:msg=json.loads(line)
        except ValueError as exc:raise AgentProtocolError('agent sent invalid JSON') from exc
        if not isinstance(msg,dict) or msg.get('type')!='action' or not isinstance(msg.get('action'),dict):
            raise AgentProtocolError('agent message is not an action')
        return msg['action']

    def close(self,failed=False):
        if failed:self.proc.kill()  # a faulty agent gets no grace period
        else:
            try:self.send({'type':'end'})
            except AgentProtocolError:pass
        try:self.proc.stdin.close()
        except OSError:pass
        try:self.proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.proc.kill();self.proc.wait()
        self.proc.stdout.close();self._err.close()
        with open(self.stderr_path,'rb') as f:return f.read(STDERR_KEEP).decode('utf-8','replace')


class ProcessLauncher:
    level='option1_process'
    def __init__(self,work_base,timeout=45):
        self.work_base=Path(work_base);self.timeout=timeout
    def wrap(self,cmd,cwd):return list(cmd)
    def open(self,cmd,stderr_path):
        cwd=tempfile.mkdtemp(prefix='agent_task_',dir=self.work_base)
        self._cwd=cwd
        return AgentSession(self.wrap(cmd,cwd),cwd,self.timeout,stderr_path)
    def cleanup(self):shutil.rmtree(self._cwd,ignore_errors=True)


# Runs inside the new namespaces, still as root, then drops to the agent account.
# Each mount is private to this task's mount namespace and disappears with it.
_INNER='for d in /tmp /var/tmp /dev/shm; do mount -t tmpfs -o size=16m,mode=1777 tmpfs "$d" || exit 97; done; ' \
       'cd /tmp || exit 98; exec setpriv --reuid="$DCH_UID" --regid="$DCH_GID" --clear-groups ' \
       '--no-new-privs --inh-caps=-all --bounding-set=-all -- "$@"'


class UserNetnsLauncher(ProcessLauncher):
    level='option2_user_netns'
    def __init__(self,work_base,user='dch-agent',timeout=45):
        super().__init__(work_base,timeout)
        if not sys.platform.startswith('linux'):raise RuntimeError('Option 2 needs Linux')
        if os.geteuid()!=0:raise RuntimeError('Option 2 must be started as root so it can create namespaces and drop to the agent account')
        for tool in ('unshare','setpriv','mount'):
            if not shutil.which(tool):raise RuntimeError(f'{tool} not found')
        try:pw=pwd.getpwnam(user)
        except KeyError as exc:raise RuntimeError(f'agent account {user} missing; run setup_isolation.sh') from exc
        if pw.pw_uid==0:raise RuntimeError('agent account must not be root')
        self.uid,self.gid=pw.pw_uid,pw.pw_gid
    def wrap(self,cmd,cwd):
        # env is passed to sh only; setpriv inherits it, and it holds nothing secret.
        return ['env',f'DCH_UID={self.uid}',f'DCH_GID={self.gid}',
                'unshare','--net','--pid','--fork','--kill-child','--mount-proc','--propagation','private','--',
                'sh','-c',_INNER,'dch-agent',*cmd]


def make_launcher(level,work_base,timeout=45,user='dch-agent'):
    if level=='process':return ProcessLauncher(work_base,timeout)
    if level=='user':return UserNetnsLauncher(work_base,user,timeout)
    raise ValueError(level)
