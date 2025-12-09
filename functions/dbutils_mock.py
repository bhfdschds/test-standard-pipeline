"""
Mock dbutils for local PySpark development outside of Databricks.
Provides stubs for commonly used dbutils functions.

Usage:
    from functions.dbutils_mock import get_dbutils
    dbutils = get_dbutils(spark)
"""

import os
from typing import Any, Dict, List, Optional


class WidgetsMock:
    """Mock for dbutils.widgets"""

    def __init__(self):
        self._widgets: Dict[str, str] = {}

    def text(self, name: str, defaultValue: str, label: str = "") -> None:
        """Create a text widget with default value"""
        if name not in self._widgets:
            self._widgets[name] = defaultValue

    def dropdown(self, name: str, defaultValue: str, choices: List[str], label: str = "") -> None:
        """Create a dropdown widget with default value"""
        if name not in self._widgets:
            self._widgets[name] = defaultValue

    def combobox(self, name: str, defaultValue: str, choices: List[str], label: str = "") -> None:
        """Create a combobox widget with default value"""
        if name not in self._widgets:
            self._widgets[name] = defaultValue

    def multiselect(self, name: str, defaultValue: str, choices: List[str], label: str = "") -> None:
        """Create a multiselect widget with default value"""
        if name not in self._widgets:
            self._widgets[name] = defaultValue

    def get(self, name: str) -> str:
        """Get widget value"""
        if name in self._widgets:
            return self._widgets[name]
        # Check environment variables as fallback
        env_value = os.environ.get(f"WIDGET_{name.upper()}")
        if env_value:
            return env_value
        raise ValueError(f"Widget '{name}' not found. Set it with widgets.text() or env var WIDGET_{name.upper()}")

    def getAll(self) -> Dict[str, str]:
        """Get all widget values"""
        return self._widgets.copy()

    def remove(self, name: str) -> None:
        """Remove a widget"""
        self._widgets.pop(name, None)

    def removeAll(self) -> None:
        """Remove all widgets"""
        self._widgets.clear()


class SecretsMock:
    """Mock for dbutils.secrets - uses environment variables"""

    def get(self, scope: str, key: str) -> str:
        """Get secret from environment variable: SECRET_{SCOPE}_{KEY}"""
        env_key = f"SECRET_{scope.upper()}_{key.upper()}"
        value = os.environ.get(env_key)
        if value is None:
            raise ValueError(f"Secret not found. Set environment variable: {env_key}")
        return value

    def getBytes(self, scope: str, key: str) -> bytes:
        """Get secret as bytes"""
        return self.get(scope, key).encode('utf-8')

    def list(self, scope: str) -> List[Dict[str, str]]:
        """List secrets in scope (returns env vars matching pattern)"""
        prefix = f"SECRET_{scope.upper()}_"
        return [{"key": k.replace(prefix, "").lower()}
                for k in os.environ.keys() if k.startswith(prefix)]

    def listScopes(self) -> List[Dict[str, str]]:
        """List all secret scopes"""
        scopes = set()
        for key in os.environ.keys():
            if key.startswith("SECRET_"):
                parts = key.split("_")
                if len(parts) >= 3:
                    scopes.add(parts[1].lower())
        return [{"name": scope} for scope in scopes]


class FSMock:
    """Mock for dbutils.fs - uses local filesystem"""

    def __init__(self, base_path: str = "/tmp/dbutils_fs"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _resolve_path(self, path: str) -> str:
        """Convert dbfs:/ paths to local paths"""
        if path.startswith("dbfs:/"):
            path = path[6:]
        elif path.startswith("/dbfs/"):
            path = path[6:]
        return os.path.join(self.base_path, path.lstrip("/"))

    def ls(self, path: str) -> List[Any]:
        """List files in directory"""
        local_path = self._resolve_path(path)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Path not found: {path}")

        results = []
        for item in os.listdir(local_path):
            item_path = os.path.join(local_path, item)
            is_dir = os.path.isdir(item_path)
            size = 0 if is_dir else os.path.getsize(item_path)
            results.append(type('FileInfo', (), {
                'path': f"dbfs:/{path.lstrip('/')}/{item}",
                'name': item,
                'size': size,
                'isDir': lambda d=is_dir: d,
                'isFile': lambda d=is_dir: not d,
            })())
        return results

    def mkdirs(self, path: str) -> bool:
        """Create directories"""
        local_path = self._resolve_path(path)
        os.makedirs(local_path, exist_ok=True)
        return True

    def rm(self, path: str, recurse: bool = False) -> bool:
        """Remove file or directory"""
        import shutil
        local_path = self._resolve_path(path)
        if os.path.isdir(local_path):
            if recurse:
                shutil.rmtree(local_path)
            else:
                os.rmdir(local_path)
        else:
            os.remove(local_path)
        return True

    def cp(self, src: str, dst: str, recurse: bool = False) -> bool:
        """Copy file or directory"""
        import shutil
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)
        if os.path.isdir(src_path):
            if recurse:
                shutil.copytree(src_path, dst_path)
            else:
                raise ValueError("Must set recurse=True for directories")
        else:
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
        return True

    def mv(self, src: str, dst: str, recurse: bool = False) -> bool:
        """Move file or directory"""
        import shutil
        src_path = self._resolve_path(src)
        dst_path = self._resolve_path(dst)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.move(src_path, dst_path)
        return True

    def put(self, path: str, contents: str, overwrite: bool = False) -> bool:
        """Write string to file"""
        local_path = self._resolve_path(path)
        if os.path.exists(local_path) and not overwrite:
            raise FileExistsError(f"File exists: {path}. Set overwrite=True")
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'w') as f:
            f.write(contents)
        return True

    def head(self, path: str, maxBytes: int = 65536) -> str:
        """Read first N bytes of file"""
        local_path = self._resolve_path(path)
        with open(local_path, 'r') as f:
            return f.read(maxBytes)


class OptionMock:
    """Mock for Scala Option type used in notebook context"""

    def __init__(self, value: Any):
        self._value = value

    def get(self) -> Any:
        """Get the value"""
        return self._value

    def getOrElse(self, default: Any) -> Any:
        """Get value or default"""
        return self._value if self._value is not None else default

    def isDefined(self) -> bool:
        """Check if value is defined"""
        return self._value is not None


class TagsMock:
    """Mock for notebook context tags"""

    def __init__(self, tags: Dict[str, str]):
        self._tags = tags

    def apply(self, key: str) -> str:
        """Get tag value by key"""
        return self._tags.get(key, "")

    def get(self, key: str) -> OptionMock:
        """Get tag as Option"""
        return OptionMock(self._tags.get(key))


class NotebookContextMock:
    """Mock for notebook context"""

    def __init__(self, notebook_path: str, username: str, extra_tags: Dict[str, str] = None):
        self._notebook_path = notebook_path
        self._username = username
        self._tags = {"user": username}
        if extra_tags:
            self._tags.update(extra_tags)

    def notebookPath(self) -> OptionMock:
        """Get the notebook path as Option"""
        return OptionMock(self._notebook_path)

    def tags(self) -> TagsMock:
        """Get notebook tags"""
        return TagsMock(self._tags)

    def apiUrl(self) -> OptionMock:
        """Get API URL"""
        return OptionMock(os.environ.get("DATABRICKS_HOST", "http://localhost"))

    def apiToken(self) -> OptionMock:
        """Get API token"""
        return OptionMock(os.environ.get("DATABRICKS_TOKEN"))


class NotebookInfoMock:
    """Mock for notebook info returned by getDbutils().notebook()"""

    def __init__(self, context: NotebookContextMock):
        self._context = context

    def getContext(self) -> NotebookContextMock:
        """Get the notebook context"""
        return self._context


class DbUtilsEntryMock:
    """Mock for the object returned by entry_point.getDbutils()"""

    def __init__(self, notebook_info: NotebookInfoMock):
        self._notebook_info = notebook_info

    def notebook(self) -> NotebookInfoMock:
        """Get notebook info"""
        return self._notebook_info


class EntryPointMock:
    """Mock for dbutils.notebook.entry_point"""

    def __init__(self, notebook_path: str, username: str):
        self._context = NotebookContextMock(notebook_path, username)
        self._notebook_info = NotebookInfoMock(self._context)
        self._dbutils_entry = DbUtilsEntryMock(self._notebook_info)

    def getDbutils(self) -> DbUtilsEntryMock:
        """Get dbutils entry object"""
        return self._dbutils_entry


class NotebookMock:
    """Mock for dbutils.notebook"""

    def __init__(self, notebook_path: str = None, username: str = None):
        # Default notebook path based on current working directory
        if notebook_path is None:
            cwd = os.getcwd()
            notebook_path = f"/Workspace/Users/{username or 'local_user'}/{os.path.basename(cwd)}/notebook"

        # Default username from environment or fallback
        if username is None:
            username = os.environ.get("USERNAME", os.environ.get("USER", "local_user@example.com"))

        self._notebook_path = notebook_path
        self._username = username
        self.entry_point = EntryPointMock(notebook_path, username)

    def exit(self, value: str) -> None:
        """Exit notebook with value"""
        print(f"[Notebook Exit] {value}")

    def run(self, path: str, timeout_seconds: int = 0, arguments: Dict[str, str] = None) -> str:
        """Run another notebook (not supported in mock)"""
        raise NotImplementedError(
            f"dbutils.notebook.run() is not supported in local development. "
            f"Attempted to run: {path}"
        )


class DBUtilsMock:
    """Main dbutils mock class"""

    def __init__(
        self,
        spark=None,
        fs_base_path: str = "/tmp/dbutils_fs",
        notebook_path: str = None,
        username: str = None
    ):
        self.widgets = WidgetsMock()
        self.secrets = SecretsMock()
        self.fs = FSMock(fs_base_path)
        self.notebook = NotebookMock(notebook_path, username)
        self._spark = spark

    def help(self) -> None:
        """Show help"""
        print("""
DBUtils Mock for Local Development
===================================
Available modules:
  - dbutils.widgets: Widget management (uses in-memory storage)
  - dbutils.secrets: Secret management (uses environment variables)
  - dbutils.fs: File system operations (uses local filesystem)
  - dbutils.notebook: Notebook operations (includes entry_point context mock)

Notebook Context:
  - dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
  - dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')

Configure via environment variables or get_dbutils() parameters:
  - NOTEBOOK_PATH: Set the mock notebook path
  - USERNAME: Set the mock username

Note: This is a mock for local development. Some features may behave
differently than in Databricks.
        """)


def get_dbutils(
    spark=None,
    fs_base_path: str = "/tmp/dbutils_fs",
    notebook_path: str = None,
    username: str = None
):
    """
    Get dbutils - returns real dbutils in Databricks, mock otherwise.

    Usage:
        from pyspark.sql import SparkSession
        from functions.dbutils_mock import get_dbutils

        spark = SparkSession.builder.getOrCreate()
        dbutils = get_dbutils(spark)

    For local development with custom notebook path:
        dbutils = get_dbutils(
            spark,
            notebook_path="/Workspace/Users/myuser/my_project/notebook",
            username="myuser@example.com"
        )

    The notebook context can then be accessed:
        path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
        user = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')
    """
    # Try to get real dbutils (works in Databricks Connect)
    try:
        from pyspark.dbutils import DBUtils
        return DBUtils(spark)
    except (ImportError, RuntimeError, Exception):
        # ImportError: pyspark.dbutils not available
        # RuntimeError: Not connected to Databricks (local Spark session)
        pass

    # Try IPython method (works in Databricks notebooks)
    try:
        import IPython
        dbutils = IPython.get_ipython().user_ns.get('dbutils')
        if dbutils is not None:
            return dbutils
    except (ImportError, AttributeError):
        pass

    # Check environment variables for notebook path and username
    if notebook_path is None:
        notebook_path = os.environ.get("NOTEBOOK_PATH")
    if username is None:
        username = os.environ.get("USERNAME", os.environ.get("USER"))

    # Return mock for local development
    print("[INFO] Using mock dbutils for local development")
    return DBUtilsMock(spark, fs_base_path, notebook_path, username)
