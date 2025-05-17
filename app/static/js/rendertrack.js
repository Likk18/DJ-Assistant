function renderTracks(tracks, containerId, onAddClick = null) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';

  // Handle empty states
  if (!tracks || tracks.length === 0) {
    let message = 'No tracks available.';
    if (containerId === 'suggested-tracks') {
      message = 'Add a track to your set to see suggestions.';
    } else if (containerId === 'dj-set') {
      message = 'Your DJ set is empty.';
    }
    container.innerHTML = `<p class="text-gray-500 italic">${message}</p>`;
    return;
  }

  // Render each track
  tracks.forEach(track => {
    const card = document.createElement('div');
    card.className = 'flex items-center gap-4 p-2 border rounded shadow';

    const img = document.createElement('img');
    img.src = track.image_url || 'https://via.placeholder.com/60';
    img.alt = `Cover for ${track.title}`;
    img.className = 'w-16 h-16 object-cover rounded';

    const info = document.createElement('div');
    info.className = 'flex-grow';

    const title = document.createElement('p');
    title.textContent = track.title;
    title.className = 'font-semibold';

    const artist = document.createElement('p');
    artist.textContent = track.artist;
    artist.className = 'text-sm text-gray-600';

    info.appendChild(title);
    info.appendChild(artist);
    card.appendChild(img);
    card.appendChild(info);

    // Add button for trending or suggested tracks
    if (onAddClick && containerId !== 'dj-set') {
      const button = document.createElement('button');
      button.textContent = 'Add';
      button.className = 'bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded';
      button.onclick = () => onAddClick(track.id);
      card.appendChild(button);
    }

    container.appendChild(card);
  });
}