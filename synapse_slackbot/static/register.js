const tabs = ['tab1', 'tab2', 'tab3'];
let activeTab = 0;

$(function() {
  bindListeners();
});

const bindListeners = function() {
  bindBackButton();
  bindNextButton();
  bindFileInput();
  bindFormSubmit();
};

const bindBackButton = function() {
  $('.back').click(function(e) {
    e.preventDefault();

    if (activeTab > 0) {
      $('.'+tabs[activeTab]).removeClass('active')
      if (activeTab === 2) {
        $('.next').removeClass('inactive');
        $('.submit').addClass('inactive');
        $('.submit').attr('disabled', true);
      }
      activeTab -= 1;
      $('.'+tabs[activeTab]).addClass('active');
    }
  });
};

const bindNextButton = function() {
  $('.next').click(function(e) {
    e.preventDefault();

    if (activeTab < 2) {
      $('.'+tabs[activeTab]).removeClass('active')
      activeTab += 1;
      $('.'+tabs[activeTab]).addClass('active')
      if (activeTab === 2) {
        $('.next').addClass('inactive');
        $('.submit').removeClass('inactive');
        $('.submit').attr('disabled', false);
      }
    }
  });
};

const bindFormSubmit = function() {
  $('form').submit(function(e) {
    e.preventDefault();

    let formData = new FormData(this);
    formData.append('file', base64);

    $.ajax({
      url: $(this).attr('action'),
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      dataType: 'json'
    })
      .done(function(data) {
        console.log(data);
      });
  });
};

var base64;

const bindFileInput = function() {
  $('#govtId').on('change', function(e){
    let base64;
    fileToBase64(this.files[0], function(e) {
      base64 = (e.target.result);
    });
  });
};

const fileToBase64 = function(file, onLoadCallback){
  const reader = new FileReader();
  reader.onload = onLoadCallback;
  return reader.readAsDataURL(file);
};
