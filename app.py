import streamlit as st
import boto3
from PIL import Image
import io
import pandas as pd
from datetime import datetime
import requests
import random
import logging
import base64
from pathlib import Path

# Configure Streamlit page
st.set_page_config(
    page_title="SheepSafe - Fårövervakning",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set up logging to terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sheepsafe")

def add_bg_image():
    image_path = "bg.jpg"
    
    try:
        # Läs in bilden och konvertera till Base64
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        # CSS för att sätta bakgrundsbilden
        background_style = f"""
        <style>
        [data-testid="stMainBlockContainer"] {{
            background-image: url(data:image/jpeg;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.8);
        }}
        
        [data-testid="stHeader"] {{
            background-color: rgba(0, 0, 0, 0);
        }}
        
        div.stApp {{
            background-color: rgba(0, 0, 0, 0);
        }}
        </style>
        """
        
        st.markdown(background_style, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Kunde inte ladda bakgrundsbild: {e}")

# Initiera session state för vargbilder
if 'last_seen_images' not in st.session_state:
    st.session_state.last_seen_images = set()

# Anropa bakgrundsfunktionen
add_bg_image()

# Layout med div-element och flexbox
st.markdown("""
<style>
    
    .header-container {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        gap: 10px;
        margin-bottom: 20px;
    }
    
    .title-column {
        flex: 2;
    }
    
    .info-column {
        flex: 1;
    }
    
    /* Resten av dina befintliga stilar */
    .integrated-box {
        border-radius: 10px;
        padding: 15px;
        height: 100%;
        overflow: hidden;
        background-color: rgba(255, 255, 255, 0.8);
    }
    
    .title-box {
        background-color: rgba(240, 248, 255, 0.9);
        border: 2px solid #3498db;
    }
    
    .weather-box {
        background-color: rgba(240, 248, 255, 0.9);
        border: 2px solid #3498db;
    }
    
    .stat-box {
        background-color: rgba(243, 229, 245, 0.9);
        border: 2px solid #9c27b0;
    }
</style>

<div class="header-container">
    <div class="title-column">
        <div class="integrated-box title-box">
            <h1>SheepSafe - Fårövervakning</h1>
        </div>
    </div>
    <div class="info-column">
        <div class="integrated-box weather-box">
            <h3>Väder</h3>
            <p><b>15°C</b>, Clear sky</p>
            <p>Luftfuktighet: 54%</p>
            <p>Vind: 6.7 m/s</p>
        </div>
    </div>
    <div class="info-column">
        <div class="integrated-box stat-box">
            <h3>Gårdsstatistik</h3>
            <p><b>Får:</b> 50 st</p>
            <p><b>Lamm:</b> 31 st</p>
            <p><b>Fodernivå:</b> 16%</p>
            <div style="background-color: #e0e0e0; border-radius: 5px; height: 10px; width: 100%;">
                <div style="background-color: #2196F3; height: 100%; width: 16%; border-radius: 5px;"></div>
            </div>
            <p>Status: ⚠️ Kritiskt låg</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Get weather data (but don't display success messages)
def get_weather():
    try:
        weather_api_url = "https://api.openweathermap.org/data/2.5/weather?q=Stockholm,se&units=metric&appid=da0f9c8d90bde7e619c3ec47766a42f4"
        response = requests.get(weather_api_url)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'], 1),
                'icon': data['weather'][0]['icon']
            }
        else:
            logger.error(f"Weather API error: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Weather fetch error: {str(e)}")
        return None

st.title("Såhär ser hagen ut idag!")
st.video("https://www.youtube.com/watch?v=iEAUoMgnRvU")

# Create a placeholder for wolf alerts
alert_placeholder = st.empty()

# AWS credentials
access_key = ''
secret_key = ''

# Sidebar for settings
with st.sidebar:
    st.header("Inställningar")
    
    location_options = ["Alla platser", "Östhage", "Norrhage", "Söderhage", "Västhage"]
    selected_location = st.selectbox("Välj plats:", location_options)
    
    
    max_images = st.slider("Max antal bilder att visa", 1, 5, 10)
    
    st.subheader("Tidsfilter")
    use_time_filter = st.checkbox("Filtrera på tid", value=False)
    
    if use_time_filter:
        start_date = st.date_input("Från datum", value=datetime.now().date())
        end_date = st.date_input("Till datum", value=datetime.now().date())
    
    # Add automatic refresh option
    auto_refresh = st.checkbox("Automatisk uppdatering", value=False)
    if auto_refresh:
        refresh_interval = st.slider("Uppdateringsintervall (sekunder)", 
                                    min_value=5, max_value=60, value=10)
    
    if st.button("Uppdatera data"):
        st.success("Data uppdateras...")

# Funktion för att hämta bilder från S3
def get_all_images_from_s3(bucket_name, today_date=None):
    try:
        if today_date is None:
            today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Lista objekt i bucketen
        response = s3_client.list_objects_v2(
            Bucket=bucket_name
        )
        
        if 'Contents' not in response:
            st.warning(f"Inga objekt hittades i bucketen {bucket_name}")
            return []
        
        # Sortera objekt efter senast modifierad (nyast först)
        objects = sorted(
            response['Contents'],
            key=lambda obj: obj['LastModified'],
            reverse=True
        )
        
        # Filtrera objekt som är bilder
        image_objects = []
        for obj in objects:
            key = obj['Key']
            last_modified = obj['LastModified']
            
            # Kolla om det är en bild baserat på filändelsen
            is_image = key.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
            
            # Kolla om nymodifierad inom senaste 24 timmarna
            is_recent = (datetime.now(last_modified.tzinfo) - last_modified).total_seconds() < 86400
            
            # Kolla om dagens datum finns i filnamnet
            contains_today = today_date in key
            
            # Prioritera bilder från idag eller nyligen modifierade
            priority = 0
            if contains_today:
                priority += 2
            if is_recent:
                priority += 1
            
            if is_image:
                image_objects.append({
                    'key': key,
                    'last_modified': last_modified,
                    'priority': priority
                })
        
        # Sortera bilder efter prioritet (högst först) och sedan efter tid (nyast först)
        image_objects.sort(key=lambda x: (x['priority'], x['last_modified']), reverse=True)
        
        return image_objects
    except Exception as e:
        st.error(f"Fel vid hämtning av bilder från S3: {str(e)}")
        return []

try:
    # Create AWS session and clients
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name='us-east-1'  
    )
    
    s3_client = session.client('s3')
    dynamodb_client = session.client('dynamodb')
    
    bucket_name = 'sheepsafe-wolves'  
    dynamodb_table = 'Wolf_Observations'  
    
    def test_aws_permissions():
        try:
            # Test S3 access
            s3_client.list_buckets()
            logger.info("✅ S3 access working")
            
            # Test bucket access
            s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"✅ Can access S3 bucket: {bucket_name}")
            
            # Test DynamoDB access
            dynamodb_client.list_tables()
            logger.info("✅ DynamoDB access working")
            
            # Test table access
            dynamodb_client.describe_table(TableName=dynamodb_table)
            logger.info(f"✅ Can access DynamoDB table: {dynamodb_table}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Permission test failed: {str(e)}")
            return False

    # Call the function (logs to terminal)
    has_permissions = test_aws_permissions()
    
   # Get observations from DynamoDB
    response = dynamodb_client.scan(
    TableName=dynamodb_table,
    Limit=100
)

    if 'Items' in response:
        logger.info(f"Retrieved {len(response['Items'])} observations from DynamoDB")
    
    # Initialize observations list
    observations = []
    
    for item in response['Items']:
        observation = {}
        
        # Extract fields (utan id)
        if 'timestamp' in item:
            observation['timestamp'] = item['timestamp'].get('S', '')
        if 'bucket' in item:
            observation['bucket'] = item['bucket'].get('S', '')
        if 'distance' in item:
            observation['distance'] = item['distance'].get('N', '')
        if 'image' in item:
            observation['image'] = item['image'].get('S', '')
        if 'label' in item:
            observation['label'] = item['label'].get('S', '')
        if 'location' in item:
            observation['location'] = item['location'].get('S', '')
        if 'message' in item:
            observation['message'] = item['message'].get('S', '')
        
        # Filtrera så att vi bara tar med faktiska vargdetektioner
        # och inte de som innehåller "No wolf detected"
        message = item.get('message', {}).get('S', '').lower()
        if ('wolf' in message or 'varg' in message) and 'no wolf' not in message and 'no varg' not in message:
            observations.append(observation)
    
    # Filter based on settings
    filtered_observations = []
    
    for obs in observations:
        # Filter by location
        if selected_location != "Alla platser" and obs.get('location') != selected_location:
            continue
        
        # Filter by time if active
        if use_time_filter and 'timestamp' in obs:
            try:
                obs_date_str = obs['timestamp'].split('T')[0]
                obs_date = datetime.strptime(obs_date_str, "%Y-%m-%d").date()
                
                if obs_date < start_date or obs_date > end_date:
                    continue
            except:
                pass
        
        filtered_observations.append(obs)
    
    # Sort observations by timestamp (newest first)
    filtered_observations.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Show number of detections
    wolf_count = len(filtered_observations)
    st.markdown(f"**Information:** Visar {wolf_count} vargdetektioner.")
    
    # Main section for data
    st.header("Vargdetektioner")
    
    # Show detailed table
    if filtered_observations:
        df = pd.DataFrame(filtered_observations)
        
        # Define columns to display (utan id och is_wolf)
        display_columns = ['timestamp', 'location', 'message', 'distance']
        display_df = df[display_columns] if all(col in df.columns for col in display_columns) else df
        
        st.dataframe(display_df)
        
        # Visa bilder    
        st.header("Dagens bilder")
        
        # Hämta alla bilder från S3
        today_str = datetime.now().strftime("%Y-%m-%d")
        s3_images = get_all_images_from_s3(bucket_name, today_str)
        
        if s3_images:
            st.success(f" Visar de {min(len(s3_images), max_images)} senaste bilderna.")
            
            # Begränsa antalet bilder som visas
            displayed_images = s3_images[:max_images]
            
            # Skapa kolumner för bilderna
            cols = st.columns(3)
            
            # Håll koll på antal lyckade bildvisningar
            successful_images = 0
            
            # Loopa igenom bilderna
            for i, img_obj in enumerate(displayed_images):
                image_key = img_obj['key']
                last_modified = img_obj['last_modified']
                
                try:
                    # Hämta bilden från S3
                    image_obj = s3_client.get_object(Bucket=bucket_name, Key=image_key)
                    image_data = image_obj['Body'].read()
                    
                    image = Image.open(io.BytesIO(image_data))
                    successful_images += 1
                    
                    col_idx = successful_images % 3
                    with cols[col_idx]:
                        # Kontrollera om bilden kan vara en vargbild baserat på filnamnet
                        is_wolf_image = 'wolf' in image_key.lower() or 'varg' in image_key.lower()
                        
                        if is_wolf_image:
                            st.markdown("### 🐺 Möjlig vargbild!")
                        
                        # Format timestamp
                        time_str = last_modified.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Visa bilden
                        st.image(image, caption=f"Uppladdad: {time_str}", use_container_width=True)
                        
                except Exception as e:
                    st.error(f"Kunde inte hämta bild {image_key}: {str(e)}")
            
            # Visa information om lyckade bildvisningar
            if successful_images == 0:
                st.warning("Kunde inte visa några bilder. Se terminalloggen för detaljer.")
            elif successful_images < len(displayed_images):
                st.warning(f"Kunde bara visa {successful_images} av {len(displayed_images)} bilder.")
        else:
            st.info("Inga bilder hittades i S3-bucketen.")
    else:
        st.warning(f"Inga observationer hittades i DynamoDB-tabellen {dynamodb_table}")
        
except Exception as e:
    logger.error(f"AWS connection error: {str(e)}")
    st.error("Det uppstod ett fel med AWS-anslutningen. Se terminalloggen för detaljer.")

# Add auto-refresh meta tag if enabled
if auto_refresh:
    st.markdown(f"""
    <script>
        setTimeout(function(){{
            window.location.reload();
        }}, {refresh_interval * 1000});
    </script>
    """, unsafe_allow_html=True)
