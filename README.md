# CMPE252-AI-ChatBot : Online Shoes Bot

A chatbot to help the customer in checking the stcok of a shoes type, return the order or check the status.


# Install dependencies
Run

```
pip install -r requirements.txt
```

# Run the bot

Train the model using 
```
rasa train
```

Then, setup the sction server in another terminal window 
```
rasa run actions
```

Talk to the bot
```
rasa shell
```

In case you're interetsed to understand how it's working under the hood, use `rasa shell --debug`


# Files
  - `data\`
    - `stories.yml` contains the stories, used for multi-turn conversation
    - `nlu.yml` contains the NLU training data
    - `rules.yml` training data used by dialogue manager which always follows the same path, used for single-turn conversation
  - `actions\`
   - `actions.py` contains custom actions
  - `domain.yml` conatins intent, actions, responses, form and entities information
  - `config.yml` training configuration for NLU pipleine

# Conversation Flows
![image](https://user-images.githubusercontent.com/90728105/166392485-d2caf8e4-4d06-45cd-b70d-a5c02f047933.png)
![image](https://user-images.githubusercontent.com/90728105/166414757-6621dc21-4b0f-4f02-af25-8fef5a037f6b.png)

  ## Happy Paths
 ![image](https://user-images.githubusercontent.com/90728105/166414710-094e3470-554d-46ce-b650-4ec5b20af443.png)
 
  
  ## Sad Paths
   ![image](https://user-images.githubusercontent.com/90728105/166414663-c487d9c9-e4c0-44dc-b590-028de11f8501.png)

      
  
  
  ## Out of scope
   This includes questions/messages, a user may but there's no user goal implemented yet. 
   For eg. Who's US president? or What is 67 + 89?
   ![image](https://user-images.githubusercontent.com/90728105/166393306-75f81132-bae2-4bc6-ba77-909d4919273b.png)
     
   ## NLU Fallback
   This is to handle low confidence incoming messages gracefuuly, where botresponds with default message.
   For eg. 

            
  
  
