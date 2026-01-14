let room = null;
let audioElement = null;
let isConnected = false;

// Wait for LiveKit client to be available
function waitForLiveKit() {
  return new Promise((resolve, reject) => {
    // Check if already loaded - correct global name is LivekitClient (lowercase 'k')
    const getLiveKit = () => {
      return (
        window.LivekitClient || // Correct case: LivekitClient
        window.LiveKitClient || // Fallback for different versions
        window.livekit ||
        window.LiveKit
      );
    };

    const livekit = getLiveKit();
    if (livekit && livekit.Room) {
      resolve(livekit);
      return;
    }

    // Wait for it to load (max 10 seconds)
    let attempts = 0;
    const maxAttempts = 100;
    const interval = setInterval(() => {
      attempts++;
      const lk = getLiveKit();
      if (lk && lk.Room) {
        clearInterval(interval);
        resolve(lk);
      } else if (attempts >= maxAttempts) {
        clearInterval(interval);
        console.error(
          'LiveKit not found. Available globals:',
          Object.keys(window).filter((k) => k.toLowerCase().includes('livekit'))
        );
        reject(
          new Error(
            'LiveKit client failed to load. Please check the browser console.'
          )
        );
      }
    }, 100);
  });
}

// Load products on page load
document.addEventListener('DOMContentLoaded', async () => {
  console.log('DOM loaded, initializing...');

  // Load products immediately (don't wait for LiveKit)
  await loadProducts();
  setupCallControls();

  // Try to load LiveKit in the background (non-blocking)
  waitForLiveKit()
    .then(() => {
      console.log('LiveKit client loaded successfully');
    })
    .catch((error) => {
      console.error('Failed to load LiveKit client:', error);
      const statusDiv = document.getElementById('callStatus');
      if (statusDiv) {
        statusDiv.textContent =
          'Warning: LiveKit client not loaded. Call feature may not work.';
        statusDiv.className = 'call-status error';
      }
    });
});

async function loadProducts() {
  try {
    console.log('Loading products...');
    const response = await fetch('/api/products');

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ error: 'Unknown error' }));
      throw new Error(
        `Failed to load products: ${errorData.error || response.statusText}`
      );
    }

    const data = await response.json();
    console.log('Products data received:', data);

    if (!data || !data.products) {
      throw new Error('Invalid product data format');
    }

    displayProducts(data.products);
  } catch (error) {
    console.error('Error loading products:', error);
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = `<div class="error" style="padding: 20px; color: #721c24; background: #f8d7da; border-radius: 8px;">
      <strong>Failed to load products:</strong><br>${error.message}<br>
      <small>Please check the browser console for more details.</small>
    </div>`;
  }
}

function displayProducts(products) {
  const grid = document.getElementById('productsGrid');

  if (!grid) {
    console.error('Products grid element not found!');
    return;
  }

  if (!products || Object.keys(products).length === 0) {
    grid.innerHTML = '<div class="error">No products available.</div>';
    return;
  }

  grid.innerHTML = '';

  for (const [category, items] of Object.entries(products)) {
    if (!items || !Array.isArray(items) || items.length === 0) {
      continue; // Skip empty categories
    }
    const card = document.createElement('div');
    card.className = 'product-card';

    const categoryTitle = document.createElement('div');
    categoryTitle.className = 'product-category';
    categoryTitle.textContent = category;
    card.appendChild(categoryTitle);

    items.forEach((item) => {
      const productItem = document.createElement('div');
      productItem.className = 'product-item';

      const name = document.createElement('div');
      name.className = 'product-name';
      name.textContent = item.name;

      const desc = document.createElement('div');
      desc.className = 'product-description';
      desc.textContent = item.description;

      const price = document.createElement('div');
      price.className = 'product-price';
      if (item.price) {
        price.textContent = `PKR ${item.price.toLocaleString('en-PK')}`;
      } else {
        price.textContent = 'Price on request';
      }

      productItem.appendChild(name);
      productItem.appendChild(desc);
      productItem.appendChild(price);
      card.appendChild(productItem);
    });

    grid.appendChild(card);
  }
}

function setupCallControls() {
  const startBtn = document.getElementById('startCallBtn');
  const endBtn = document.getElementById('endCallBtn');
  const statusDiv = document.getElementById('callStatus');

  if (!startBtn) {
    console.error('Start call button not found!');
    return;
  }

  if (!endBtn) {
    console.error('End call button not found!');
    return;
  }

  console.log('Setting up call controls...');

  startBtn.addEventListener('click', async () => {
    console.log('Start call button clicked');
    try {
      await startCall();
    } catch (error) {
      console.error('Error starting call:', error);
      updateStatus('error', 'Failed to start call: ' + error.message);
    }
  });

  endBtn.addEventListener('click', async () => {
    console.log('End call button clicked');
    await endCall();
  });

  console.log('Call controls set up successfully');
}

async function startCall() {
  if (isConnected) {
    return;
  }

  const startBtn = document.getElementById('startCallBtn');
  const endBtn = document.getElementById('endCallBtn');
  const statusDiv = document.getElementById('callStatus');

  startBtn.disabled = true;
  updateStatus('connecting', 'Connecting to Shop Whisper...');

  try {
    // Ensure LiveKit is loaded
    const LiveKit = await waitForLiveKit();
    if (!LiveKit || !LiveKit.Room) {
      console.error('LiveKit object:', LiveKit);
      console.error(
        'Available properties:',
        LiveKit ? Object.keys(LiveKit) : 'none'
      );
      throw new Error('LiveKit Room class not found. Please refresh the page.');
    }

    // Generate room name
    const roomName = `shop-${Date.now()}`;
    const participantName = `Customer-${Math.random()
      .toString(36)
      .substr(2, 9)}`;

    // Get token from server
    const response = await fetch('/api/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        room_name: roomName,
        participant_name: participantName,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to get access token');
    }

    const { token, url, room_name } = await response.json();

    if (!url) {
      throw new Error('LiveKit URL not configured');
    }

    // Start agent for this room
    await fetch('/api/start-agent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        room_name: room_name,
      }),
    });

    // Connect to LiveKit room
    console.log('Creating Room with LiveKit:', LiveKit);
    console.log('LiveKit.Room:', LiveKit.Room);
    room = new LiveKit.Room({
      adaptiveStream: true,
      dynacast: true,
    });
    console.log('Room instance created successfully');

    room.on('participantConnected', (participant) => {
      console.log('Participant connected:', participant.identity);
      console.log('Participant details:', {
        identity: participant.identity,
        name: participant.name,
        metadata: participant.metadata,
      });
      if (
        participant.identity.startsWith('shop-whisper') ||
        participant.name === 'shop-whisper-agent'
      ) {
        updateStatus(
          'connected',
          'Connected! Shop Whisper is ready to help you.'
        );
      }
    });

    // Log all room state changes
    room.on('stateChanged', (state) => {
      console.log('Room state changed:', state);
    });

    // Log when we connect
    room.on('connected', () => {
      console.log('Room connected successfully');
      console.log('Room name:', room.name);
      console.log('Local participant:', room.localParticipant.identity);
    });

    room.on('trackSubscribed', (track, publication, participant) => {
      if (track.kind === 'audio') {
        const audioEl = track.attach();
        audioEl.setAttribute('autoplay', 'true');
        audioEl.setAttribute('playsinline', 'true');

        const container = document.getElementById('audioContainer');
        container.innerHTML = '';
        container.appendChild(audioEl);
        container.style.display = 'block';
      }
    });

    room.on('disconnected', () => {
      console.log('Disconnected from room');
      isConnected = false;
      updateStatus('', 'Call ended');
      startBtn.disabled = false;
      endBtn.style.display = 'none';
      startBtn.style.display = 'inline-flex';
    });

    await room.connect(url, token);
    isConnected = true;

    // Enable microphone
    // Enable microphone for the local participant
    await room.localParticipant.setMicrophoneEnabled(true);

    startBtn.style.display = 'none';
    endBtn.style.display = 'inline-flex';
    updateStatus('connected', 'Connected! Shop Whisper is ready to help you.');
  } catch (error) {
    console.error('Connection error:', error);
    updateStatus('error', 'Connection failed: ' + error.message);
    startBtn.disabled = false;
    isConnected = false;
    throw error;
  }
}

async function endCall() {
  if (room && isConnected) {
    await room.disconnect();
    isConnected = false;
  }
}

function updateStatus(type, message) {
  const statusDiv = document.getElementById('callStatus');
  statusDiv.className = `call-status ${type}`;
  statusDiv.textContent = message;
}
