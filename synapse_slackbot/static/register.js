$(function() {
  bindListeners();
});

const TABS = ['tab0', 'tab1', 'tab2'];
let activeTab = 0;

const activeTabSelector = function(tabNumber) {
  return '.' + TABS[activeTab];
};

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
      $(activeTabSelector()).removeClass('active');

      if (activeTab === 2) {
        hideSubmit();
      }

      activeTab -= 1;
      $(activeTabSelector()).addClass('active');
    }
  });
};

const bindNextButton = function() {
  $('.next').click(function(e) {
    e.preventDefault();

    const errors = checkValidationErrors();
    if (errors.length > 0) {
      return;
    }

    if (activeTab < 2) {
      $(activeTabSelector()).removeClass('active');
      activeTab += 1;
      $(activeTabSelector()).addClass('active');

      if (activeTab === 2) {
        showSubmit();
      }
    }
  });
};

const hideSubmit = function() {
  $('.next').removeClass('inactive');
  $('.submit').addClass('inactive');
  $('.submit').attr('disabled', true);
};

const showSubmit = function() {
  $('.next').addClass('inactive');
  $('.submit').removeClass('inactive');
  $('.submit').attr('disabled', false);
};

const bindFormSubmit = function() {
  $('form').submit(function(e) {
    e.preventDefault();

    const errors = checkValidationErrors();
    if (errors.length > 0) {
      return;
    }

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

const checkValidationErrors = function() {
  if (activeTab === 0) {
    return tab0Validations();
  }
  else if (activeTab === 1) {
    return tab1Validations();
  }
  else if (activeTab === 2) {
    return tab2Validations();
  }
};

const tab0Validations = function() {
  const name = $('input[name=name]').val(),
    birthday = $('input[name=birthday]').val(),
    email = $('input[name=email]').val(),
    phone = $('input[name=phone]').val(),
    addressStreet = $('input[name=address_street]').val(),
    addressCity = $('input[name=address_city]').val(),
    addressState = $('input[name=address_state]').val(),
    addressZip = $('input[name=address_zip]').val();

  const errors = [];

  if (name.split(' ').length < 2) {
    errors.push('Name must be at least 2 words.');
  }
  if (birthday.length < 10) {
    errors.push('Invalid date of birth.');
  }
  if (!/\S+@\S+\.\S+/.test(email)) {
    errors.push('Invalid email address.');
  }
  if (phone.length < 10) {
    errors.push('Phone number must be at least 10 digits.');
  }
  if (addressStreet.split(' ').length < 2) {
    errors.push('Invalid street address.');
  }
  if (addressCity.length < 2) {
    errors.push('Invalid address city.');
  }
  if (addressState.length < 2) {
    errors.push('Address state should be at least 2 letters.');
  }
  if (addressZip.length < 5) {
    errors.push('ZIP code should be at least 5 letters.');
  }
  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const tab1Validations = function() {
  const ssn = $('input[name=ssn]').val(),
    govtId = $('input[name=govtId').val();

  const errors = [];
  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const tab2Validations = function() {
  const accountNumber = $('input[name=account_number]').val(),
    routingNumber = $('input[name=routing_number]').val();

  const errors = [];
  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const renderErrors = function(errors) {
  $('.alert').empty();
  const errorElements = errors.map(function(error){
    return $('<p class="alert-message">' + error + '</p>');
  });
  $('.alert').append(errorElements);
  $('.alert').removeClass('valid');
  $('.alert').addClass('invalid');
};
