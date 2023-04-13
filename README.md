# ECE1779
Intro to Cloud Computing

## Assignments

### A1
This web application is designed to run a mask detection model on images in order to identify whether people detected in the image are wearing masks. The application provides a full user experience, enabling registered users the ability to login, upload images to detect masks, and view all of their previously uploaded images categorized by the number of people wearing masks. Additionally, users can also reset their password in case they have forgotten it. The application offers additional user management capabilities specific to the administrator, who can register new users.

### A2
Webapp from A1 extended to add a separate manager webapp which can launch EC2 instances to run the user webapp and perform load balancing. It offers manual control over the worker pool and also allows setting an auto-scaler policy. The auto-scaler runs as a background process monitoring average CPU utilization and automatically adds or removes workers to the pool. Worker utilization can be monitored from charts on the manager app's homepage. The user app is enhanced to save images in S3, use RDS as its database, push HTTP requests to CloudWatch metrics, and allow deleting users and uploaded images.

### A3
Webapp that presents auctions solicited from multiple web sources and allows searching and filtering the results.

## Contact:
Denis Noskov - denis.noskov@mail.utoronto.ca

Sheran Cardoza - sheran.cardoza@mail.utoronto.ca

Amarpreet Singh - amarkbr.singh@mail.utoronto.ca
