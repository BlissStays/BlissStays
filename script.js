
// Minimal interactions
const openGallery = () => {
  const overlay = document.querySelector('#galleryOverlay');
  overlay?.classList.add('open');
}
const closeGallery = () => {
  document.querySelector('#galleryOverlay')?.classList.remove('open');
}
document.addEventListener('click', (e)=>{
  if(e.target.id === 'galleryOverlay') closeGallery();
});
