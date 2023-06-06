function  mtoString(v) {
		 
		if (v == null || v == '') return '';
		var res=v.toString().trim();
		return res;
			}



  function tableTransform() {
            $("table").each(function () {

                var $this = $(this);
                var newrows = [];
                $this.find("tbody tr, thead tr").each(function () {
                    var i = 0;
                    $(this).find("td, th").each(function () {
                        i++;
                        if (newrows[i] === undefined) {
                            newrows[i] = $("<tr></tr>");
                        }
                        newrows[i].append($(this));
                    });
                });
                $this.find("tr").remove();
                $.each(newrows, function () {
                    $this.append(this);
                });
            });
           
        }