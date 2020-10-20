# Fibonacci Serverless

## Assignment Description

Please implement a serverless service using any cloud provider of your choice, which calculates and displays results for the following algorithms:

* Calculating a Fibonacci number F(n) with the value of n provided by the user.
* The Ackermann function A(m,n) with values of m and n provided by the user.
* The factorial of a non-negative integer n provided by the user.

The results per function should be calculated separately and user's input should be validated. The exercise has 
two bonus parts. The first is to implement a more efficient version for one or more of the functions in parallel
to the 'naive' implementation and show the difference in the monitoring dashboard. The second part is to provide a
deployment artifact for your service, like an Ansible playbook, or another medium of deployment of your choice.

#### Solution approach

The proposed solution uses recursive serverless functions which are run on Google's Cloud Run.

#### Setup:
Install Google Cloud SDK, create an account and a project, then run:
```
$ cd 4_fibonacci_serverless/
$ export GCP_PROJECT="<your_project>"
$ ./scripts/build-deploy.sh
```

This will print out the service url endpoint, you can then send GET requests to:
* /ackermann/<n_value>/<m_value>
* /fibonacci/<index>
* /factorial/<n_value>
* /factorial_parallel/<n_value>