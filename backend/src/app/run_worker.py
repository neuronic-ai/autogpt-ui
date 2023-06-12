from arq import run_worker

from app.worker.main import WorkerSettings

if __name__ == "__main__":
    run_worker(WorkerSettings)  # type: ignore
