// script.js

const upload = document.getElementById('upload');
const container = document.getElementById('storyContainer');
const viewer = document.getElementById('viewer');
const viewerImage = document.getElementById('viewerImage');
const viewerVideo = document.getElementById('viewerVideo');
const caption = document.getElementById('caption');
const progress = document.getElementById('progress');
const sound = document.getElementById('storySound');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const reactionResult = document.getElementById('reactionResult');

let stories = [];
let currentIndex = -1;
let timeout;

// Upload stories
upload.addEventListener('change', (e) => {
  for (let file of e.target.files) {
    const url = URL.createObjectURL(file);
    const type = file.type.startsWith("video") ? "video" : "image";
    const story = document.createElement('div');
    story.className = 'story';
    story.style.backgroundImage = `url(${type === 'video' ? 'https://via.placeholder.com/70x70?text=%F0%9F%8E%A5' : url})`;
    story.dataset.url = url;
    story.dataset.type = type;
    story.dataset.caption = file.name;
    story.addEventListener('click', () => openStory(stories.indexOf(story)));
    container.appendChild(story);
    stories.push(story);
  }
});

// Show story
function openStory(index) {
  clearTimeout(timeout);
  currentIndex = index;
  const story = stories[index];
  const url = story.dataset.url;
  const type = story.dataset.type;
  const text = story.dataset.caption;

  caption.textContent = text;
  sound.play();
  viewer.classList.remove('hidden');
  progress.style.animation = 'none';
  void progress.offsetWidth;
  progress.style.animation = 'progressAnim 5s linear forwards';

  story.classList.add('seen');

  if (type === 'image') {
    viewerImage.src = url;
    viewerImage.classList.remove('hidden');
    viewerVideo.classList.add('hidden');
  } else {
    viewerVideo.src = url;
    viewerVideo.classList.remove('hidden');
    viewerImage.classList.add('hidden');
  }

  timeout = setTimeout(() => {
    if (currentIndex + 1 < stories.length) {
      openStory(currentIndex + 1);
    } else {
      closeViewer();
    }
  }, 5000);
}

function closeViewer() {
  viewer.classList.add('hidden');
  viewerImage.src = '';
  viewerVideo.src = '';
  reactionResult.textContent = '';
  clearTimeout(timeout);
}

prevBtn.onclick = () => {
  if (currentIndex > 0) openStory(currentIndex - 1);
};
nextBtn.onclick = () => {
  if (currentIndex + 1 < stories.length) openStory(currentIndex + 1);
};

function react(emoji) {
  reactionResult.textContent = `You reacted with ${emoji}`;
}

// Enable sound on interaction
sound.currentTime = 0;
sound.play().catch(e => {
  console.log("Autoplay prevented, waiting for user interaction");
});

document.getElementById("enableSound").onclick = () => {
  sound.play().catch(e => console.log("Still blocked"));
};

// Add text to story
function addTextToStory() {
  const text = document.getElementById('storyTextInput').value.trim();
  const overlay = document.getElementById('textOverlay');
  const color = document.getElementById('textColor').value;
  const size = document.getElementById('textSize').value;

  if (text) {
    overlay.textContent = text;
    overlay.style.display = 'block';
    overlay.style.color = color;
    overlay.style.fontSize = size;
  }
}

// Drag-and-drop text overlay
const overlay = document.getElementById('textOverlay');
overlay.addEventListener('dragstart', (e) => {
  e.dataTransfer.setData('text/plain', null);
});
document.getElementById('viewer').addEventListener('dragover', (e) => {
  e.preventDefault();
});
document.getElementById('viewer').addEventListener('drop', (e) => {
  const x = e.clientX;
  const y = e.clientY;
  overlay.style.position = 'absolute';
  overlay.style.left = `${x - overlay.offsetWidth / 2}px`;
  overlay.style.top = `${y - overlay.offsetHeight / 2}px`;
});

// Send message
function sendMessage() {
  const messageInput = document.getElementById("messageInput");
  const messageLog = document.getElementById("messageLog");

  const msg = messageInput.value.trim();
  if (msg === "") return;

  const msgEl = document.createElement("div");
  msgEl.textContent = `You: ${msg}`;
  messageLog.appendChild(msgEl);

  messageInput.value = "";
}