from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

AWS_KEY = os.environ.get('AWS_KEY')
AWS_SECRET = os.environ.get('AWS_SECRET')

# Setup the default args according to the project instructions
default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'catchup_by_default': False,
    'email_on_retry': False
}

# TODO: What's the desired schedule?
dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='@daily'
        )

start_operator = DummyOperator(
    task_id='Begin_execution',
    dag=dag
)

################################################# Table Creation tasks ################################
create_staging_events_table_task = PostgresOperator(
    task_id = "Create Staging Events Table, if not exists",
    dag = dag,
    postgres_conn_id = "redshift",
    sql = SqlQueries.staging_events_table_create
)

create_staging_songs_table_task = PostgresOperator(
    task_id = "Create Staging Songs Table, if not exists",
    dag = dag,
    postgres_conn_id = "redshift",
    sql = SqlQueries.staging_songs_table_create
)

create_time_table_task = PostgresOperator(
    task_id = "Create Time Table, if not exists",
    dag = dag,
    postgres_conn_id = "redshift",
    sql = SqlQueries.time_table_create
)

create_user_table_task = PostgresOperator(
    task_id = "Create User Table, if not exists",
    dag = dag,
    postgres_conn_id = "redshift",
    sql = SqlQueries.user_table_create
)

create_artist_table_task = PostgresOperator(
    task_id = "Create Artist Table, if not exists",
    dag = dag,
    postgres_conn_id = "redshift",
    sql = SqlQueries.artist_table_create
)

create_song_table_task = PostgresOperator(
    task_id = "Create Song Table, if not exists",
    dag = dag,
    postgres_conn_id = "redshift",
    sql = SqlQueries.song_table_create
)

create_songplay_table_task = PostgresOperator(
    task_id = "Create Songplay Table, if not exists",
    dag = dag,
    postgres_conn_id = "redshift",
    sql = SqlQueries.songplay_table_create
)

wait_for_table_creation_op = DummyOperator(
    task_id = "Wait for table creation",
    dag = dag
)

#################################################  S3 To Staging Tables Tasks ################################
stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag
)

###########################################  Loading to Fact and Dim Tables Tasks #########################
load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag
)

######################################################## Quality Check ###########################################



run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag
)

end_operator = DummyOperator(
    task_id='Stop_execution',
    dag=dag
)

# Define the dependencies of tasks
start_operator >> create_staging_events_table_task
start_operator >> create_staging_songs_table_task
start_operator >> create_time_table_task
start_operator >> create_user_table_task
start_operator >> create_artist_table_task
start_operator >> create_song_table_task
start_operator >> create_songplay_table_task

create_staging_events_table_task >> wait_for_table_creation_op
create_staging_songs_table_task >> wait_for_table_creation_op
create_time_table_task >> wait_for_table_creation_op
create_time_table_task >> wait_for_table_creation_op
create_user_table_task >> wait_for_table_creation_op
create_artist_table_task >> wait_for_table_creation_op

wait_for_table_creation_op >> stage_events_to_redshift
wait_for_table_creation_op >> stage_songs_to_redshift

stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table >> run_quality_checks
load_songplays_table >> load_song_dimension_table >> run_quality_checks
load_songplays_table >> load_artist_dimension_table >> run_quality_checks
load_songplays_table >> load_time_dimension_table >> run_quality_checks

run_quality_checks >> end_operator


