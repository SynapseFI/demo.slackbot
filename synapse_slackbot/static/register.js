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
  bindInputsFilled();
};

const bindInputsFilled = function() {
  $('form').bind('keyup click change', function() {
    const $inputs = $(activeTabSelector() + ' input');
    let filled = true;
    $inputs.each(function(index, element) {
      if ($(element).val() == '') {
        filled = false;
      }
    });
    if (filled) {
      enableNextButton();
    }
    else {
      disableNextButton();
    }
  });
};

const bindBackButton = function() {
  $('.back').click(function(e) {
    e.preventDefault();
    clearAlerts();

    if (activeTab === 0) {
      disableBackButton();
    }
    else {
      $(activeTabSelector()).removeClass('active');
      enableBackButton();

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
    clearAlerts();

    const errors = checkValidationErrors();
    if (errors.length > 0) {
      return;
    }

    enableBackButton();
    disableNextButton();

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

const enableBackButton = function() {
  $('.back').removeAttr('disabled');
};

const disableBackButton = function () {
  $('.back').attr('disabled', true);
};

const enableNextButton = function() {
  $('.next').removeAttr('disabled');
};

const disableNextButton = function() {
  $('.next').attr('disabled', true);
};

const hideSubmit = function() {
  $('.next').removeClass('inactive');
  enableNextButton();
  $('.submit').addClass('inactive');
  $('.submit').attr('disabled', true);
};

const showSubmit = function() {
  $('.next').addClass('inactive');
  disableNextButton();
  $('.submit').removeClass('inactive');
  $('.submit').removeAttr('disabled');
};

const bindFormSubmit = function() {
  $('form').submit(function(e) {
    e.preventDefault();
    clearAlerts();

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

    renderAlert('Please wait...', 'pending');
  });
};

const handleSuccess = function(data) {
  clearAlerts();

  renderAlert(data['message'], 'valid');
};

const handleFailure = function(data) {
  clearAlerts();

  const errorText = JSON.parse(data['responseText'])['message'];
  renderAlert(errorText, 'invalid');
};

let base64;

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
  const fields = {
    $name: $('input[name=name]'),
    $birthday: $('input[name=birthday]'),
    $email: $('input[name=email]'),
    $phone: $('input[name=phone]'),
    $addressStreet: $('input[name=address_street]'),
    $addressCity: $('input[name=address_city]'),
    $addressState: $('input[name=address_state]'),
    $addressZip: $('input[name=address_zip]')
  };

  $.each(fields, function(_, $input) {
    $input.removeClass('invalid');
  });

  const errors = [];

  if (fields.$name.val().split(' ').length < 2) {
    errors.push('Name must be at least 2 words.');
    fields.$name.addClass('invalid');
  }
  if (fields.$birthday.val().length < 10) {
    errors.push('Invalid date of birth.');
    fields.$birthday.addClass('invalid');
  }
  if (!/\S+@\S+\.\S+/.test(fields.$email.val())) {
    errors.push('Invalid email address.');
    fields.$email.addClass('invalid');
  }
  if (fields.$phone.val().length < 10) {
    errors.push('Phone number must be at least 10 digits.');
    fields.$phone.addClass('invalid');
  }
  if (fields.$addressStreet.val().split(' ').length < 2) {
    errors.push('Invalid street address.');
    fields.$addressStreet.addClass('invalid');
  }
  if (fields.$addressCity.val().length < 2) {
    errors.push('Invalid address city.');
    fields.$addressCity.addClass('invalid');
  }
  if (fields.$addressState.val().length < 2) {
    errors.push('Address state should be at least 2 letters.');
    fields.$addressState.addClass('invalid');
  }
  if (fields.$addressZip.val().length < 5) {
    errors.push('ZIP code should be at least 5 letters.');
    fields.$addressZip.addClass('invalid');
  }
  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const tab1Validations = function() {
  const fields = {
    $ssn: $('input[name=ssn]'),
    $govtId: $('input[name=govt_id')
  };

  $.each(fields, function(_, $input) {
    $input.removeClass('invalid');
  });

  const errors = [];

  if (fields.$ssn.val().length < 4) {
    errors.push('SSN must be at least 4 digits.');
    fields.$ssn.addClass('invalid');
  }
  if (fields.$govtId.val().length < 4) {
    errors.push('Photo ID image required.');
    fields.$govtId.addClass('invalid');
  }

  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const tab2Validations = function() {
  const fields = {
    $accountNumber: $('input[name=account_number]'),
    $routingNumber: $('input[name=routing_number]')
  };

  $.each(fields, function(_, $input) {
    $input.removeClass('invalid');
  });

  const errors = [];

  if (fields.$accountNumber.val() < 6) {
    errors.push('Account number must be at least 6 digits.');
    fields.$accountNumber.addClass('invalid');
  }
  if (fields.$routingNumber.val().length !== 9) {
    errors.push('Routing number must be 9 digits.');
    fields.$routingNumber.addClass('invalid');
  }

  if (errors.length > 0) {
    renderErrors(errors);
  }

  return errors;
};

const renderErrors = function(errors) {
  const $errorElements = errors.forEach(function(errorText){
    renderAlert(errorText, 'invalid');
  });
};

const clearAlerts = function() {
  const $alert = $('.alert');
  $alert.empty();
  $alert.removeClass('valid');
  $alert.removeClass('invalid');
};

const renderAlert = function(message, status) {
  const $message = alertMessage(message),
    $alert = $('.alert');
  $alert.append($message);
  $alert.removeClass('valid invalid pending');
  $alert.addClass(status);
};

const alertMessage = function(text) {
  return $('<p class="alert-message">' + text + '</p>');
};
