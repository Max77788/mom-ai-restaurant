from celery_config import make_celery
from flask import Flask, jsonify, session
import ast
import datetime
import uuid
from openai import OpenAI
from deep_translator import GoogleTranslator
import time
from time import sleep

# Initialize a new Flask app just for the context
flask_app = Flask(__name__)

# Create Celery instance
celery = make_celery(flask_app)

def generate_code():
    return str(uuid.uuid4())[:7]


def get_assistants_response(user_message, language, thread_id, assistant_id, menu_file_id, client_openai, payment_on, list_of_all_items, list_of_image_links, unique_azz_id, res_currency, discovery_mode=False):
    client = client_openai
    print("Entered assistants response function")

    # Initialize the GoogleTranslator
    translator = GoogleTranslator(source='auto', target='en')
    
    if language != "en":
        # Translate the user input to English
        translated_user_message = translator.translate(user_message)
        print("Translated user message in English: ", translated_user_message)  # Should output the translated text in English
        print("--------------------------------------------------------")
    else:
        translated_user_message = user_message

    """
    # Define the language of the message
    thread_id_language = client.beta.threads.create().id
    
    prompt_to_translator_define_lang = f'''
    Define the language of this message:
    {user_message}
    '''

    print("\n\nPrompt we send to translator: ", prompt_to_translator_define_lang, "\n\n")

    response = client.beta.threads.messages.create(thread_id=thread_id_language,
                                                   role="user",
                                                   content=prompt_to_translator_define_lang)

    run = client.beta.threads.runs.create(thread_id=thread_id_language,
                                          assistant_id=MOM_AI_LANGUAGE_DETECTOR)

    start_time = time.time()
    while True:
        if time.time() - start_time > 25:
            response = 'O-oh, little issues when forming the response, repeat the message now'
            return jsonify({"response": response}), 0

        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_language,
                                                       run_id=run.id)
        if run_status.status == "completed":
            print(f"\n\nTokens used by restaurant assistant: {run_status.usage.total_tokens}\n\n")
            messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_language)
            formatted_language_info = messages_gpt_json.data[0].content[0].text.value
            print(f"\nFormatted translator output (Output from MOM AI TRANSLATOR): {formatted_language_info}\n")

            parsed_formatted_language_info = ast.literal_eval(formatted_language_info.strip())
            language_code = parsed_formatted_language_info["language_code"]
            language_adj = parsed_formatted_language_info["language_adj"]
            break
        elif run_status.status == "failed":
            print("Run status, ", run_status)
            print("Language detection failed")
            raise Exception("Language detection failed")
        sleep(0.5)  # Reduce sleep duration

    
    # Translating the items
    thread_id_translator = client.beta.threads.create().id
    
    prompt_to_translator_translate_items = f'''
    Translate this list of items into {language_adj} or leave it unchanged if it is already in {language_adj}:
    {list_of_all_items}
    RETURN THE RESPONSE IN THE FORMAT OF LISTS OF LISTS.
    '''

    print("prompt we sent to translate menu items, ", prompt_to_translator_translate_items)

    response = client.beta.threads.messages.create(thread_id=thread_id_translator,
                                                   role="user",
                                                   content=prompt_to_translator_translate_items)
    run = client.beta.threads.runs.create(thread_id=thread_id_translator,
                                          assistant_id=MOM_AI_LANGUAGE_DETECTOR)

    start_time = time.time()
    while True:
        if time.time() - start_time > 45:
            response = 'O-oh, little issues when forming the response, repeat the message now'
            return jsonify({"response": response}), 0
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_translator,
                                                       run_id=run.id)
        if run_status.status == "completed":
            print(f"\n\nTokens used by restaurant assistant: {run_status.usage.total_tokens}\n\n")
            messages_gpt_translator = client.beta.threads.messages.list(thread_id=thread_id_translator)
            formatted_translator_info = messages_gpt_translator.data[0].content[0].text.value
            print(f"\nFormatted translator output (Output from MOM AI TRANSLATOR): {formatted_translator_info}\n")

            parsed_formatted_translator_info = ast.literal_eval(formatted_translator_info.strip())
            list_of_all_items = parsed_formatted_translator_info["translated_list_of_items"]
            break
        elif run_status.status == "failed":
            print("Run status, ", run_status)
            print("Language detection failed")
            raise Exception("Language detection failed")
        sleep(0.5)  # Reduce sleep duration
    print("translated with GPT in: ", time.time()-start_time)

    #print("List of items returned by menu items translator: ", list_of_all_items)

    list_of_items_with_links = [t + [l] for t, l in zip(list_of_all_items, list_of_image_links)]
    #print("\n\nList of items with links: ", list_of_items_with_links, "\n\n")
    """

    #language_adj = "English"
    #list_of_items_with_links = [t + (l,) for t, l in zip(list_of_all_items, list_of_image_links)]

    '''
    user_message_enhanced = f"""
    Role: You are the best restaurant assistant who serves customers and register orders in the system
    
    Context: The customer asks you the question or writes the statement - your goal is to provide the response appropriately in {language_adj} language
    facilitating order taking. To your knowledge base is attached the vector store provided for you. The currency in which prices of the items are specified is Euro.
    Recommend, suggest and anyhow use only and only the items specified in this file. Do not mention other dishes whatsoever! Do not include source in the final info.
    If the user confirms the order set up the status of the message 'requires_action'. Be sure to initiate action regardless of the language in which you communicate.
    Confirm the order and trigger the action as fast as possible in the context of the particular order. 
    Make sure that the item you suggest are from this list presented in the format (item name, item ingredients, item price). Also include html img elemets for each dish you present, if the image link is present. 
    Make the maximal width of image to be 170px and height to be auto. URGENT! PRESENT THE IMAGE ONLY USING HTML IMG ELEMENTS WITH THE MAXIMAL WIDTH OF 170px:
    {list_of_items_with_links}
    Do not spit out all these items at once, refer to them only once parsed the attached menu to be sure that you are suggesting the right items.
    Never trigger the action after the first customer's message. I.e. when there is only one user's message in the thread.
    Never include more than 7 items in the response.

    Task: Here is the current user's message, respond to it in this language - {language_adj}:
    {translated_user_message}  
    ALWAYS PROVIDE THE USER WITH A CLEAR CALL TO ACTION AT THE END OF THE RESPONSE!    
    (in the context of ongoing order taking process and attached to your knowledge base and to this message menu file)
    """
    '''
    
    # print("\n\nUser message enhanced after translator: \n\n", user_message_enhanced, "\n\n")
    messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
    
    
    if discovery_mode:
       message_to_compare_menu_items = f"""
        Before generating the message ensure that the items you consider suggesting and the items which the user asks for are 
        from this list and use the images from this list:
        {list_of_all_items} 
        Provide the image strictly in the format: <img src="[image_link]" alt="Image of [item name]" width="170" height="auto"> 
        Provide the images as much as possible.
        Do not trigger any action in response. Do not trigger any action in response. Do not trigger any action in response.
        Inform the customer about the fact that he won't be able to order via this chat and he is able to discover the menu and get personalized recommendations.
        The prices of the items are in this currency: {res_currency}
        """
    else:
        message_to_compare_menu_items = f"""
        Before generating the message ensure that the items you consider suggesting and the items which the user asks for are 
        from this list and use the images from this list:
        {list_of_all_items} 
        Provide the image strictly in the format: <img src="[image_link]" alt="Image of [item name]" width="170" height="auto"> 
        Provide the images as much as possible.
        The prices of the items are in this currency: {res_currency}
        """
 
    print("Message to compare menu items: ", message_to_compare_menu_items)

    response = client.beta.threads.messages.create(thread_id=thread_id,
                                                   role="user",
                                                   content=translated_user_message,
                                                   attachments=[{
                                                       "file_id":menu_file_id,
                                                       "tools":[{"type":"file_search"}]
                                                   }])
    
    if discovery_mode:
        if len(list(messages_gpt)) < 2:
            print("Nif-nif1")
            user_message = f"""
            Context:  You only provide the oral assistance on restaurant menu to the customer.  Do not trigger any action in response. Do not trigger any action in response. Do not trigger any action in response.
            Inform the customer about the fact that he won't be able to order via this chat and he is able to discover the menu and get personalized recommendations.   
            The prices of the items are in this currency: {res_currency}

            Customer\'s message: {translated_user_message}    
            """
        else:
            print("Naf-naf1")
            user_message = f"""
            Do not trigger any action in response. Do not trigger any action in response. Do not trigger any action in response.
            The prices of the items are in this currency: {res_currency}
            
            Customer\'s message: {translated_user_message}    
            """
        
        response = client.beta.threads.messages.create(thread_id=thread_id,
                                                   role="user",
                                                   content=user_message,
                                                   attachments=[{
                                                       "file_id":menu_file_id,
                                                       "tools":[{"type":"file_search"}]
                                                   }])
    
    run = client.beta.threads.runs.create(thread_id=thread_id,
                                          assistant_id=assistant_id,
                                          additional_instructions=message_to_compare_menu_items,
                                          temperature=1)
    
    start_time = time.time()
    while True:
        if time.time() - start_time > 25:
            response = 'O-oh, little issues when forming the response, repeat the message now'
            return jsonify({"response": response}), 0
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                       run_id=run.id)
        print(run_status.status)
        
        if run_status.status == 'completed':
            print(f"\n\nTokens used by restaurant assistant: {run_status.usage.total_tokens}\n\n")
            print("--------------------------------------------------------")

            total_tokens_used = run_status.usage.total_tokens
            break
        elif run_status.status == 'failed' or run_status.status == 'incomplete':
            print("Run failed.")
            last_error = run.last_error if "last_error" in run else None
            if last_error:
                print("Last Error:", last_error)
            else:
                print("No errors reported for this run.")

            #print(f"\n\nRun steps: \n{run_steps}\n")
            response = 'O-oh, little issues, repeat the message now'
            return jsonify({"response": response}), 0
        elif run_status.status == "requires_action":
            if discovery_mode:
                print("Action interrupted because of discovery mode.")
                run = client.beta.threads.runs.cancel(
                    thread_id=thread_id,
                    run_id=run.id
                    )
                no_action_response = "Please, type in the other message as I can't proceed with the placement of the order. I am not entitled to do that."
                return no_action_response, 0 
            print("Action in progress...")

            messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
            #print(f"Messages retrieved in action step {messages_gpt}")  # debugging line

            joined_messages_of_assistant = ""
            messages_gpt_list = list(messages_gpt)
            messages_gpt_list.reverse()

            pattern = r"Task: Here is the current user's message, respond to it:\n\s*(.*?)\s*\(in the context of"
            
            for message in messages_gpt_list:
                if message.role == 'assistant':
                    joined_messages_of_assistant += f"\nAssistant:\n{message.content[0].text.value}\n"
                if message.role == 'user':
                    match = re.search(pattern, message.content[0].text.value, re.DOTALL)
                    if match:
                        user_message = match.group(1).strip()
                        joined_messages_of_assistant += f"\nCustomer:\n{user_message}\n"
                    else:
                        joined_messages_of_assistant += f"\nCustomer:\n{message.content[0].text.value}\n"

            print(f"\nRetrieved all messages with Summary from convo: {joined_messages_of_assistant}\n")

            summary_to_convert = f"""
            These are all messages of the assistant from the chat with client. 
            From the following messages find the last one which summarizes agreed upon order and retrieve items stated in the final confirmed summary:
            {joined_messages_of_assistant}
            Ensure that the found items are part of this list of items presented in the format (item name, item ingredients, item price):
            {list_of_all_items}
            """

            print(f"Summary to convert sent to MOM AI JSON: {summary_to_convert}")  # debugging line
            

            thread_id_json = client.beta.threads.create().id
            print(f"JSON assistant thread {thread_id_json}")

            response = client.beta.threads.messages.create(thread_id=thread_id_json,
                                                           role="user",
                                                           content=summary_to_convert)

            run_json = client.beta.threads.runs.create(thread_id=thread_id_json,
                                                       assistant_id=MOM_AI_JSON_LORD_ID)

            json_start_time = time.time()
            while True:
                if time.time() - json_start_time > 25:
                    response = 'O-oh, little issues when forming the response, repeat the message now'
                    return jsonify({"response": response}), 0

                run_status = client.beta.threads.runs.retrieve(thread_id=thread_id_json,
                                                               run_id=run_json.id)
                if run_status.status == 'completed':
                    messages_gpt_json = client.beta.threads.messages.list(thread_id=thread_id_json)
                    print(f"\n\nTokens used by JSON assistant: {run_status.usage.total_tokens}\n\n")
                    total_tokens_used_JSON = run_status.usage.total_tokens
                    total_tokens_used = total_tokens_used_JSON
                    
                    formatted_json_order = messages_gpt_json.data[0].content[0].text.value
                    print(f"\nFormatted JSON Order (Output from MOM AI JSON LORD): {formatted_json_order}\n")

                    # Get the conversion rate from USD to EUR (you can change to any currencies)
                    if res_currency != 'EUR':
                        rate = c.convert(1, res_currency, 'EUR')
                    else:
                        rate = 1
                    
                    parsed_formatted_json_order = ast.literal_eval(formatted_json_order.strip())
                    items_ordered = parsed_formatted_json_order["items_ordered"]
                    session["items_ordered"] = items_ordered
                    # print(f"Setup the items ordered on assistant response! {parsed_formatted_json_order['items']}")
                   
                    order_id = generate_code()
                    current_utc_timestamp = time.time()

                    # Convert the timestamp to a datetime object
                    utc_datetime = datetime.utcfromtimestamp(current_utc_timestamp)

                    # Format the datetime object to a human-readable string
                    human_readable_time_format = utc_datetime.strftime('%Y-%m-%d %H:%M')


                    if items_ordered and payment_on:
                        db_items_cache[unique_azz_id].insert_one({"data": items_ordered, "id": order_id, "timestamp": current_utc_timestamp})

                    if payment_on:
                        total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"
                        
                        total_price_EUR = f"{float(total_price)*rate:.2f}"

                        session["currency"] = res_currency
                        session["currency_rate"] = rate

                        
                        link_to_payment_buffer = url_for("payment_buffer", unique_azz_id=unique_azz_id, id=order_id)
                        print(link_to_payment_buffer)

                        clickable_link = f'<a href={link_to_payment_buffer} style="color: #c0c0c0;" target="_blank">Press here to proceed</a>'
                        response_cart = f"Order formed successfully. Please, follow this link to finish the purchase: {clickable_link}"
                        # translator.translate()
                        return link_to_payment_buffer, total_tokens_used
                    else:
                        total_price = f"{sum(item['quantity'] * item['price'] for item in items_ordered):.2f}"
                        
                        total_price_EUR = f"{float(total_price)*rate:.2f}"

                        session["currency"] = res_currency
                        session["currency_rate"] = rate

                        session["total_price_EUR"] = total_price_EUR
                        session["total_price_NATIVE"] = total_price

                        session["order_id"] = order_id
                        session['access_granted_no_payment_order'] = True

                        order_to_pass = {"items":[{'name':item['name'], 'quantity':item['quantity']} for item in items_ordered], 
                        "orderID":order_id,
                        "timestamp": human_readable_time_format,
                        "total_paid": total_price,
                        "total_paid_EUR": total_price_EUR,
                        "mom_ai_restaurant_assistant_fee": 0,
                        "paypal_fee": 0,
                        "paid":"NOT PAID",
                        "published":True}
    
                        db_order_dashboard[unique_azz_id].insert_one(order_to_pass)
                        # print("\n\nInserted the order in db_order_dashboard with if ", unique_azz_id, "\n\n")
                        
                        string_of_items = transform_orders_to_string(items_ordered)

                        no_payment_order_finish_message = f"Thank you very much! You ordered {string_of_items} and total is {total_price} {res_currency}\nCome to the restaurant and pick up your meal shortly. Love💖\n**PLEASE SAVE THIS: Your order ID is {order_id}**"
                        
                        restaurant_instance = collection.find_one({"unique_azz_id":unique_azz_id})
                        all_ids_chats = restaurant_instance.get("notif_destin", [])

                        session["order_confirm_access_granted"] = True
                        
                        for chat_id in all_ids_chats:
                            send_telegram_notification(chat_id)
                        session["suggest_web3_bonus"] = True

                        return no_payment_order_finish_message, total_tokens_used 
                if run_status.status == 'failed':
                    print("Run of JSON assistant failed.")
                    last_error = run_json.last_error if "last_error" in run else None
                    if last_error:
                        print("Last Error:", last_error)
                    else:
                        print("No errors reported for this run.")

                    #print(f"\n\nRun steps: \n{run_steps}\n")
                    response = 'O-oh, little issues, repeat the message now'
                    return jsonify({"response": response}), 0

        sleep(0.5)  # Reduce sleep duration
                    
    messages_gpt = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages_gpt.data[0].content[0].text.value

    # _, voice_tokens_used = generate_short_voice_output(response, language)
    
    # total_tokens_used += voice_tokens_used

    """
    joined_messages_of_user = ""
    messages_gpt_list = list(messages_gpt)
    messages_gpt_list.reverse()

    pattern = r"Task: Here is the current user's message, respond to it:\n\s*(.*?)\s*\(in the context of"
    
    for message in messages_gpt_list:
        #if message.role == 'assistant':
            #joined_messages_of_assistant += f"\nAssistant:\n{message.content[0].text.value}\n"
        if message.role == 'user':
            match = re.search(pattern, message.content[0].text.value, re.DOTALL)
            if match:
                user_message = match.group(1).strip()
                joined_messages_of_user += f"{user_message}\n"
            else:
                joined_messages_of_user += f"{message.content[0].text.value}"

    print("Joined messages of user: ", joined_messages_of_user)
    print("--------------------------------------------------------")

    
    language_of_user_message = detect(joined_messages_of_user)
    """
      
    print("Raw message output from gpt: ", response)
    print("--------------------------------------------------------")
    print(f"Language into which we will, probably, translate the message: {language}")
    print("--------------------------------------------------------")
    if not language == "en":
        # Initialize the GoogleTranslator
        translator = GoogleTranslator(source='auto', target=language)

        # Translate the user input to English
        response = translator.translate(response)
        print("Translated GPTs message in user message language in English: ", response)
        print("--------------------------------------------------------")
    
    
        
    return response, total_tokens_used



@celery.task
def add(x, y):
    return x + y


