import streamlit as st
from song_dl.audio import generate_spectrogram
from song_dl.io import DownloadMetadata, add_download_data, get_all_downloads

from song_dl.paths import DOWNLOAD_DIR
from song_dl.youtube import url_to_mp3, get_video_title

# Initialize session state variables
if "all_metadata" not in st.session_state:
    st.session_state.all_metadata = get_all_downloads()
if "url_to_name" not in st.session_state:
    st.session_state.url_to_name = {
        download.url: download.title
        for download in st.session_state.all_metadata.values()
    }
if "download_queue" not in st.session_state:
    st.session_state.download_queue = []
if "downloaded_files" not in st.session_state:
    st.session_state.downloaded_files = [
        (d.url, d.save_path) for d in st.session_state.all_metadata.values()
    ]
if "current_download" not in st.session_state:
    st.session_state.current_download = None
if "is_downloading" not in st.session_state:
    st.session_state.is_downloading = False
if "spectrogram" not in st.session_state:
    st.session_state.spectrogram = None


def add_to_queue():
    """Add URL to download queue"""
    url = st.session_state.url_input
    print(f"Found {url=}")
    if url:
        st.session_state.url_input = ""  # Clear input field
        st.session_state.download_queue.append(url)

    # Get name of the song, add it to the dictionary.
    st.session_state.url_to_name[url] = get_video_title(url)


def process_current_download():
    """Process the current download in the main thread"""
    if st.session_state.is_downloading and st.session_state.current_download:
        # # Show progress bar
        # st.text(f"Downloading: {st.session_state.current_download}")
        # progress_bar = st.progress(st.session_state.download_progress)

        # Complete the current download
        save_path = url_to_mp3(st.session_state.current_download, DOWNLOAD_DIR)

        song_metadata = DownloadMetadata(
            url=st.session_state.current_download,
            title=st.session_state.url_to_name[st.session_state.current_download],
            source="youtube",
            save_path=save_path,
            artist=None,
            album=None,
        )
        # Update status
        add_download_data(song_metadata)
        st.session_state.all_metadata[song_metadata.url] = song_metadata
        st.session_state.downloaded_files.append(
            (song_metadata.url, song_metadata.save_path)
        )
        st.session_state.is_downloading = False
        st.session_state.current_download = None
        st.session_state.download_progress = 0

        # Force a rerun to update the UI
        st.rerun()


def start_next_download():
    """Start the next download if one is available"""
    if not st.session_state.is_downloading and st.session_state.download_queue:
        # Get the next URL
        url = st.session_state.download_queue[0]
        st.session_state.download_queue.remove(url)

        # Update status
        st.session_state.is_downloading = True
        st.session_state.current_download = url
        st.session_state.download_progress = 0

        # Force a rerun to start the download
        st.rerun()


def get_display_name(url: str) -> str:
    if url not in st.session_state.url_to_name:
        st.session_state.url_to_name[url] = get_video_title(url)
    display_name = st.session_state.url_to_name[url]
    return display_name


def store_spectrogram(url: str):
    img = generate_spectrogram(st.session_state.all_metadata[url].save_path)
    st.session_state.spectrogram = img


def select_download(url):
    """Store the selected download in session state"""
    st.toast(f"Selected: {url}")
    store_spectrogram(url)


# App title
st.title("song-dl")

# Create a two-column layout
left_col, right_col = st.columns([1, 1])

with left_col:
    # URL input with Enter key support
    st.text_input("yt url:", key="url_input", on_change=add_to_queue)

    # Add button
    # st.button("Add to Queue", on_click=add_to_queue)

    # Display current download
    if st.session_state.current_download:
        st.subheader("Currently Downloading")
        st.text(get_display_name(st.session_state.current_download))
        st.progress(st.session_state.download_progress)

    # Display image
    if st.session_state.spectrogram is not None:
        st.subheader("spectrogram")
        st.image(st.session_state.spectrogram, use_container_width=True)

with right_col:
    # st.subheader("Download Queue")

    # Style with custom HTML and CSS
    st.markdown(
        """
    <style>
    .download-item {
        padding: 8px 12px;
        margin: 4px 0px;
        border-radius: 4px;
        font-family: monospace;
    }
    .current {
        background-color: black;
        color: white;
        font-weight: bold;
    }
    .pending {
        background-color: #f0f2f6;
        color: #808080;
    }
    .completed {
        background-color: white;
        color: #008000;
        border: 1px solid #e6e6e6;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Display downloaded files (completed)
    if st.session_state.downloaded_files:
        for i, (url, filename) in enumerate(st.session_state.downloaded_files):
            display_name = get_display_name(url)
            # st.markdown(
            #     f"""
            # <div class="download-item completed" onclick="window.location.href='#select_download_{i}'>
            #     ✓ {display_name}
            # </div>
            # """,
            #     unsafe_allow_html=True,
            # )
            # Add a key to trigger the callback
            st.button(
                f"""
                ✓ {display_name}
                """,
                key=f"select_download_{i}",
                on_click=select_download,
                args=(url,),
                # label_visibility="collapsed",
            )

    # Display current download (highlighted)
    if st.session_state.current_download:
        display_name = get_display_name(st.session_state.current_download)
        st.markdown(
            f"""
        <div class="download-item current">
            ⟳ {display_name}
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Display pending downloads (greyed out)
    if st.session_state.download_queue:
        for url in st.session_state.download_queue:
            display_name = get_display_name(url)
            st.markdown(
                f"""
            <div class="download-item pending">
                ⋯ {display_name}
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Show empty state
    if (
        not st.session_state.downloaded_files
        and not st.session_state.current_download
        and not st.session_state.download_queue
    ):
        st.markdown(
            """
        <div style="color: #808080; text-align: center; padding: 20px;">
            No downloads in queue
        </div>
        """,
            unsafe_allow_html=True,
        )

# Wait until everything is displayed to handle downloads.
# Handle current download
if st.session_state.is_downloading:
    process_current_download()
else:
    start_next_download()

# # Add a refresh button at the bottom
# if st.button("Refresh Status"):
#     st.rerun()
