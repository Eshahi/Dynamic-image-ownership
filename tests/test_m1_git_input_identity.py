"""Real temporary Git repos; no scientific inputs and no byte rewriting."""
import hashlib,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from m1_git_input_identity import verify_git_input

class GitIdentityTests(unittest.TestCase):
    def test_crlf_working_bytes_lf_blob_and_changed_content(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
            git('init','-q');git('config','user.name','Synthetic Test');git('config','user.email','fixture@example.invalid')
            (root/'.gitattributes').write_bytes(b'*.json text eol=lf\n')
            file=root/'config.json';file.write_bytes(b'{\n  "fixture": true\n}\n')
            git('add','.');git('commit','-qm','fixture')
            commit=git('rev-parse','HEAD');lf_blob=git('rev-parse',commit+':config.json')
            file.write_bytes(b'{\r\n  "fixture": true\r\n}\r\n')
            expected=hashlib.sha256(file.read_bytes()).hexdigest()
            receipt=verify_git_input(file,commit,root,expected)
            self.assertEqual(receipt['working_sha256'],expected);self.assertEqual(receipt['git_blob_sha1'],lf_blob)
            self.assertIn(b'\r\n',file.read_bytes())
            with self.assertRaises(ValueError):verify_git_input(file,commit,root,'0'*64)
            file.write_bytes(b'{\r\n  "fixture": false\r\n}\r\n')
            with self.assertRaises(ValueError):verify_git_input(file,commit,root,hashlib.sha256(file.read_bytes()).hexdigest())
    def test_foreign_path_or_ambiguous_commit_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);file=root/'f';file.write_bytes(b'x')
            with self.assertRaises(ValueError):verify_git_input(file,'HEAD',root,hashlib.sha256(b'x').hexdigest())
            with self.assertRaises(ValueError):verify_git_input(file,'a'*40,root/'other',hashlib.sha256(b'x').hexdigest())

if __name__=='__main__':unittest.main()
