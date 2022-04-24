# CMPE252-AI-ChatBot : Online Shoes Bot

A chatbot to help the customer in checking the stcok of a shoes type, return the order or check the status.


# Install dependencies
Run

```
pip install -r requirements.txt
```

# Run the bot

Train the model using  ```rasa train```

Then, setup the sction server in another terminal window 
```rasa run actions```

Talk to the bot
```rasa shell```

In case you're interetsed to understand how it's working under the hood, use rasa shell --debug


# Files
  - `data\`
    - `stories.yml` contains the stories
    - `nlu.yml` contains the NLU training data
    - `ules.yml` contains the rules, the bot responds to
  - `actions\`
   - `actions.py` contains custom actions
  - `domain.yml` conatins intent, actions, responses, form and entities information
  - `config.yml` training configuration for NLU pipleine
