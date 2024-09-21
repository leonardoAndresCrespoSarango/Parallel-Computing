import random
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm  # Importa tqdm para la barra de progreso


driver = webdriver.Chrome()

try:
    # Abre YouTube
    driver.get("https://www.youtube.com")

    # Encuentra el cuadro de búsqueda
    search_box = driver.find_element(By.NAME, "search_query")

    # Escribe el nombre del YouTuber a buscar
    youtuber_name = "AuronPlay"  # Cambia por el nombre del YouTuber que deseas buscar
    search_box.send_keys(youtuber_name)

    # Presiona Enter para realizar la búsqueda
    search_box.send_keys(Keys.RETURN)

    # Espera unos segundos para que los resultados carguen
    time.sleep(5)

    # Busca el enlace del canal que coincida con el nombre exacto del YouTuber
    try:
        # Encuentra todos los elementos del canal
        channel_elements = driver.find_elements(By.ID, "channel-title")

        # Itera sobre los elementos encontrados para verificar el nombre exacto
        for channel in channel_elements:
            if channel.text.strip().lower() == youtuber_name.strip().lower():
                channel.click()
                break
        else:
            print("No se encontró el canal exacto")
    except Exception as e:
        print(f"No se pudo encontrar el canal: {e}")

    # Espera unos segundos para que la página del canal cargue completamente
    time.sleep(5)

    # Navega a la sección de "Videos"
    try:
        # Encuentra el enlace de la pestaña "Videos" y haz clic en él
        videos_tab = driver.find_element(By.XPATH, "//a[@href and contains(@href, '/videos')]")
        driver.execute_script("arguments[0].click();", videos_tab)
    except Exception as e:
        print(f"No se pudo navegar a la pestaña de videos: {e}")

    # Espera unos segundos para que los videos carguen
    time.sleep(5)

    # Encuentra todos los enlaces de los videos en la página actual
    try:
        video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')

        # Asegúrate de que haya videos en la lista
        if video_elements:
            # Selecciona un video aleatorio de la lista
            random_video = random.choice(video_elements)

            # Obtiene el enlace del video aleatorio
            video_url = random_video.get_attribute("href")
            print(f"URL del video seleccionado: {video_url}")
    except Exception as e:
        print(f"Error: {e}")
except Exception as e:
    print(f"error: {e}")
try:
    driver.get(video_url)
    driver.maximize_window()  # Maximiza la ventana para asegurarse de que todos los elementos sean visibles
    time.sleep(2)  # Espera para cargar la página completamente

    # Obtener el título del video
    title = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.title.style-scope.ytd-video-primary-info-renderer'))
    ).text
    print(f"Título del video: {title}")

    # Scroll hasta el final de la página para cargar los comentarios
    SCROLL_PAUSE_TIME = 2
    CYCLES = 20  # Número de veces para hacer scroll
    html = driver.find_element(By.TAG_NAME, 'html')

    # Configura tqdm para mostrar la barra de progreso
    with tqdm(total=CYCLES, desc="Cargando comentarios") as pbar:
        for _ in range(CYCLES):
            html.send_keys(Keys.END)
            time.sleep(SCROLL_PAUSE_TIME)
            pbar.update(1)  # Actualiza la barra de progreso

    # Espera adicional para asegurarse de que todos los comentarios se carguen
    time.sleep(5)

    # Extraer los elementos de los comentarios
    comment_elems = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#content-text'))
    )
    all_comments = [elem.text for elem in comment_elems]

    # Escribir los comentarios en un archivo JSON
    output_file = 'yt_comments.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_comments, f, indent=4, ensure_ascii=False)

    print(f"\nSe han extraído {len(all_comments)} comentarios y se han guardado en '{output_file}'.")

except Exception as e:
    print(f"Error al intentar extraer comentarios: {str(e)}")

finally:
    # Cerrar el navegador al finalizar
    if 'driver' in locals():
        driver.quit()
