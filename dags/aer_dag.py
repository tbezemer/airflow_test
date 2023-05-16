from datetime import datetime, timedelta
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator

with DAG(
    "AER",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "email": ["airflow@example.com"],
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="",
    schedule=timedelta(hours=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id="git_pull",
        bash_command=dedent(
            """
        cd ~/Desktop/airflow_test/git_cache;
        if [ -d "./test_app" ] 
        then
            echo "Git repo exists, cd'ing and pulling"
            cd ./test_app
            git pull
        else
            echo "Git repo does not exists, cloning"
            git clone https://github.com/tbezemer/test_app.git
        fi
        echo "Current commit hash: $(git rev-parse --short HEAD)"
        """
        ),
        retries=3,
    )
    t2 = BashOperator(
        task_id="update_dependencies",
        bash_command=dedent(
            """
        cd ~/Desktop/airflow_test/git_cache/test_app;
        if [ ! -d "./venv" ] 
        then
            python3 -m venv venv
        fi
        source ./venv/bin/activate
        pip install -e ".[dev]"
        """
        ),
    )
    t3 = BashOperator(
        task_id="test_suite",
        bash_command=dedent(
            """
        cd ~/Desktop/airflow_test/git_cache/test_app;
        source ./venv/bin/activate
        pytest
        """
        ),
    )

    tBPS = BashOperator(
        task_id="BPS",
        depends_on_past=False,
        bash_command=dedent(
            """
        cd ~/Desktop/airflow_test/git_cache/test_app;
        source ./venv/bin/activate
        testapp run -d BPS
        """
        ),
    )

    tVBS = BashOperator(
        task_id="VBS",
        depends_on_past=False,
        bash_command=dedent(
            """
        cd ~/Desktop/airflow_test/git_cache/test_app;
        source ./venv/bin/activate
        testapp run -d VBS
        """
        ),
    )

    t1.doc_md = dedent(
        """\
    #### Task Documentation
    You can document your task using the attributes `doc_md` (markdown),
    `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    rendered in the UI's Task Instance Details page.
    ![img](http://montcs.bloomu.edu/~bobmon/Semesters/2012-01/491/import%20soul.png)
    **Image Credit:** Randall Munroe, [XKCD](https://xkcd.com/license.html)
    """
    )

    dag.doc_md = (
        __doc__  # providing that you have a docstring at the beginning of the DAG; OR
    )
    dag.doc_md = """
    This is a documentation placed anywhere
    """  # otherwise, type it like this

    t1 >> t2 >> t3 >> [tBPS, tVBS]

if __name__ == "__main__":
    dag.test()
