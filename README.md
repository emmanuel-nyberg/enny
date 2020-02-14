# Bot for great financial gain.

![](https://melmagazine.com/wp-content/uploads/2019/07/Screen-Shot-2019-07-31-at-5.47.12-PM.png)


# Running enny as a lambda function.

After cloning this project, get yourself a free API key from [Alpha Vantage](https://www.alphavantage.co/) and save it somewhere.

Then get [pipenv](https://github.com/pypa/pipenv) through your most preferred method. Build your virtualenv and run a shell in it:

    pipenv install
    pipenv shell

Now things get moderately tricky. Get an AWS account and start a free instance of a MySQL-compliant RDS database. Click the "Internet acces" box since you need to be able to reach it from your laptop for testing purposes. Also click "advanced options" and create a starting database with the name "enny".
Deploy enny by simply running zappa. This will give you a decent starting environment but you will need some VPC fancy stuff.

    zappa init
    zappa deploy dev

Now we need to give the Lambda outgoing/incoming access to the Internet so it can fetch data from Alpha Vantage and still contact our RDS database.
In the AWS console, go to ```VPC Services```. First you need to create an Internet Gateway from the menu to the left. Attah it to your existing VPC.
Next, go to "Subnets" and create two new subnets within the VPC created by Zappa. Tag one with "Internet access" and the other with "Private". 
Go to "Route tables" and create a route table for your Internet subnet. Put in your Internet gateway as target for 0.0.0.0/0.
Now go to "NAT Gateways" in the menu to the left and create a NAT Gateway for your VPC. Create a route table for it and associate it with your "private" subnet.

Now go into your zappa_settings.json and enter your two subnets in the "subnets" hash.
This should make for smooth sailing.

Lastly, go into the Lambda dashboard and find your Lambda. In the "Environment Variables" menu, enter these values:
    ENNY_APIKEY: The API key from Alpha Vantage
    ENNY_DB_HOST: The full URL for your DB
    ENNY_DB_PASSWORD: The admin password you got when creating your DB.

Now you can run ```collect_lambda.sh``` in order to collect fresh stonks.
This will take a while so make some coffee and watch Chinese Cooking Demystified on Youtube.