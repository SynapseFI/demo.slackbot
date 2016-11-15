const TABS = ['tab1', 'tab2', 'tab3'];
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
    validateTabInputs(activeTab);

    if (activeTab > 0) {
      $(activeTabSelector).removeClass('active');

      if (activeTab === 2) {
        hideSubmit();
      }

      activeTab -= 1;
      $(activeTabSelector).addClass('active');
    }
  });
};

const hideSubmit = function() {
  $('.next').removeClass('inactive');
  $('.submit').addClass('inactive');
  $('.submit').attr('disabled', true);
};

const bindNextButton = function() {
  $('.next').click(function(e) {
    e.preventDefault();
    validateTabInputs(activeTab);

    if (activeTab < 2) {
      $(activeTabSelector).removeClass('active');

      activeTab += 1;

      if (activeTab === 2) {
        showSubmit();
      }

      $(activeTabSelector).addClass('active');
    }
  });
};

const showSubmit = function() {
  $('.next').addClass('inactive');
  $('.submit').removeClass('inactive');
  $('.submit').attr('disabled', false);
};

const bindFormSubmit = function() {
  $('form').submit(function(e) {
    e.preventDefault();
    validateTabInputs(activeTab);

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
        handleSuccess(data);
      })
      .fail(function(data) {
        handleFailure(data);
      });
  });
};

const handleSuccess = function(data) {
  const message = data['message'];
  $('#alertMessage').text(data['message']);
  $('.alert').removeClass('invalid');
  $('.alert').addClass('valid');
};

const handleFailure = function(data) {
  const message = JSON.parse(data['responseText'])['message'];
  $('#alertMessage').text(message);
  $('.alert').removeClass('valid');
  $('.alert').addClass('invalid');
};

const validateTabInputs = function(tabNumber) {
  const inputs = $('.tab1 input');
};

const activeTabSelector = function(tabNumber) {
  return '.tab' + TABS[activeTab];
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
