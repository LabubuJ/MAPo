window.HELP_IMPROVE_VIDEOJS = false;

var INTERP_BASE = "./static/interpolation/stacked";
var NUM_INTERP_FRAMES = 240;

var interp_images = [];
function preloadInterpolationImages() {
  for (var i = 0; i < NUM_INTERP_FRAMES; i++) {
    var path = INTERP_BASE + '/' + String(i).padStart(6, '0') + '.jpg';
    interp_images[i] = new Image();
    interp_images[i].src = path;
  }
}

function setInterpolationImage(i) {
  var image = interp_images[i];
  image.ondragstart = function() { return false; };
  image.oncontextmenu = function() { return false; };
  $('#interpolation-image-wrapper').empty().append(image);
}

function updateSequenceImages(value) {
  const frameNumber = Math.min(Math.max(parseInt(value), 73), 76);
  const paddedNumber = frameNumber.toString().padStart(5, '0');
  const modules = ['dejitter_3', '+cur', 'jitter'];
  
  modules.forEach(module => {
    const img = document.getElementById(`${module}-image`);
    if (img) {
      img.src = `./static/images/MAPo/ablation_show/jitter_show/flame_salmon_frag3/processed/bbox/${module}/${paddedNumber}.png`;
    }
  });
}

// 预加载序列图片
function preloadSequenceImages() {
  const modules = ['dejitter_3', '+cur', 'jitter'];
  const imageCache = {};

  for (let i = 73; i <= 76; i++) {
    const paddedNumber = i.toString().padStart(5, '0');
    modules.forEach(module => {
      const img = new Image();  
      img.src = `./static/images/MAPo/ablation_show/jitter_show/flame_salmon_frag3/processed/bbox/${module}/${paddedNumber}.png`;
      imageCache[`${module}-${i}`] = img;
    });
  }
  return imageCache;
}

$(document).ready(function() {
    // Check for click events on the navbar burger icon
    $(".navbar-burger").click(function() {
      $(".navbar-burger").toggleClass("is-active");
      $(".navbar-menu").toggleClass("is-active");
    });

    var defaultCarouselOptions = {
      slidesToScroll: 1,
      slidesToShow: 3,
      loop: true,
      infinite: true,
      autoplay: false,
      autoplaySpeed: 3000,
    };

    var defaultCarousels = bulmaCarousel.attach('#results-carousel', defaultCarouselOptions);

    preloadInterpolationImages();

    $('#interpolation-slider').on('input', function(event) {
      setInterpolationImage(this.value);
    });
    setInterpolationImage(0);
    $('#interpolation-slider').prop('max', NUM_INTERP_FRAMES - 1);

    bulmaSlider.attach();

    // 为序列滑块添加事件监听
    const sequenceSlider = document.getElementById('sequence-slider');
    if (sequenceSlider) {
        sequenceSlider.addEventListener('input', function() {
            updateSequenceImages(this.value);
        });
        
        // 初始化显示
        updateSequenceImages(sequenceSlider.value);
    }
});
