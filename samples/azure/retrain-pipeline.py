import kfp.dsl as dsl
from kubernetes import client as k8sc

@dsl.pipeline(
  name='Retrain pipeline on Azure',
  description='A pipeline that retrains then serves model on Azure.'
)
def sequential_pipeline():
  """A pipeline that retrains then serves model on Azure."""

  op1 = dsl.ContainerOp(
     name='retrain',
     image='ritazh/image-retrain-kubecon:1.9-gpu',
     arguments=[
          '--how_many_training_steps', 10,
          '--bottleneck_dir', '/tmp/bottlenecks',
          '--model_dir', '/tmp/inception',
          '--summaries_dir', 's3://mybucket/models/myjob2/training_summaries/baseline',
          '--output_graph', 's3://mybucket/models/myjob2/retrained_graph.pb',
          '--output_labels', 's3://mybucket/models/myjob2/retrained_labels.txt',
          '--saved_model_dir', 's3://mybucket/models/myjob2/export/inception/1',
          '--image_dir', 'images',
     ],
     file_outputs={'output': 'myjob2'}
  ).add_env_variable(
        k8sc.V1EnvVar(
            name='TF_MODEL_DIR', 
            value='s3://mybucket/models/myjob2',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='TF_EXPORT_DIR', 
            value='inception',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='TF_TRAIN_STEPS', 
            value='200',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='TF_BATCH_SIZE', 
            value='100',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='TF_LEARNING_RATE', 
            value='0.01',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='AWS_ACCESS_KEY_ID', 
            value='minio',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='AWS_SECRET_ACCESS_KEY', 
            value='minio123',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='AWS_DEFAULT_REGION', 
            value='us-east-1',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='AWS_REGION', 
            value='us-east-1',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_REGION', 
            value='us-east-1',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_USE_HTTPS', 
            value='0',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_VERIFY_SSL', 
            value='0',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_ENDPOINT', 
            value='10.0.18.85:9000',
  )).set_gpu_limit(1)

  op2 = dsl.ContainerOp(
     name='inception',
     image='elsonrodriguez/model-server:1.6',
     command=['/usr/bin/tensorflow_model_server'],
     arguments=[
        '--port', 9000,
        '--model_name', 'inception',
        '--model_base_path', 's3://mybucket/models/%s/export/inception/' % op1.output,
     ]
  ).add_env_variable(
        k8sc.V1EnvVar(
            name='AWS_ACCESS_KEY_ID', 
            value='minio',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='AWS_SECRET_ACCESS_KEY', 
            value='minio123',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='AWS_REGION', 
            value='us-east-1',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_REGION', 
            value='us-east-1',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_USE_HTTPS', 
            value='0',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_VERIFY_SSL', 
            value='0',
  )).add_env_variable(
        k8sc.V1EnvVar(
            name='S3_ENDPOINT', 
            value='10.0.18.85:9000',
  ))

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(sequential_pipeline, __file__ + '.tar.gz')
