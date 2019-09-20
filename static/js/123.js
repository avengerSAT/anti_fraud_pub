window.onload = function() {
    var inputs = document.getElementsByTagName('input');
    for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].type == 'text') {
        inputs[i].onchange = function() {
          this.value = this.value.replace(/^\s+/, '').replace(/\s+$/, '');
          this.id = this.id.replace(/^\s+/, '').replace(/\s+$/, '');
          this.name = this.name.replace(/^\s+/, '').replace(/\s+$/, '');
        };
      }
    }
  }


