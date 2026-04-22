# AWS Deployment Guide 🚀

This guide explains how to properly configure AWS S3 for the machine learning models and host your application on AWS EC2. This combination satisfies the cloud computing microproject requirements.

## Part 1: Setting up the S3 Artifact Registry

1. **Log in to the AWS Console** and navigate to **S3**.
2. **Create a Bucket**:
   - Provide a globally unique name (e.g., `medqa-mlops-models-2026`).
   - Keep defaults (ACLs disabled, Block all public access).
3. **Get IAM Credentials**:
   - Navigate to **IAM (Identity and Access Management)**.
   - Go to Users -> Select your user (or create a new one).
   - Go to "Security credentials" and **Create an Access Key**.
   - Save the `Access Key ID` and `Secret Access Key`.

4. **Add to `.env` File**:
   Create a `.env` file in the root of your project directory locally and on the server.
   ```ini
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_S3_BUCKET=your_bucket_name
   AWS_REGION=us-east-1
   ```

5. **Test S3 Locally**:
   Run the model training script locally. It will upload the models to your S3 bucket!
   ```bash
   python train_model.py
   ```

---

## Part 2: Setting up the EC2 Instance

1. **Launch EC2 Instance**:
   - Select **Ubuntu Server 24.04 LTS**.
   - Instance Type: `t2.micro` or `t3.micro` (Free Tier eligible).
   - Key Pair: Create a new key pair and download it (e.g., `my-aws-key.pem`).
   - Network Settings: Allow SSH (Port 22) and Custom TCP rules for Port **8000** (FastAPI) and Port **8501** (Streamlit).

2. **Automated Deployment**:
   Make sure you modify the permissions on your `.pem` key file first:
   ```bash
   chmod 400 my-aws-key.pem
   ```

   Run the deployment script provided in the repository from your local machine, passing your key and your EC2 instance's public IP address.
   ```bash
   # Make sure the script is executable
   chmod +x deploy_ec2.sh

   # Deploy!
   EC2_IP="YOUR.EC2.IP.ADD" KEY_PEM="path/to/my-aws-key.pem" ./deploy_ec2.sh
   ```

3. **Verify App is Running**:
   Once the script finishes, your app will be securely accessing S3 and serving requests from EC2!
   - Frontend: `http://YOUR.EC2.IP.ADD:8501`
   - Backend API: `http://YOUR.EC2.IP.ADD:8000/docs`
