		 $(document).ready(function () {

            $("#btnTpVertical").on("click", function () {
                tableTransform();
            });

            $("th, td").on("click", function () {
                if (!$(this).get(0).hasAttribute('title'))
				{
                    $(this).attr("title", $(this).html() );
                    
				}
                $(this).tooltip("show");
            });

            $("#aCollapse").on("click", function () {
                if ($('#aCollapse i').hasClass("fa-plus")) {
                    developperTout();
                    setCookie("OpOpen", "oui", 7);
                }
                else {
                    reduireTout();
                    delCookie("OpOpen");
                }
            });
            reduireTout();
            //tableTransform();
        });

        function reduireTout() {
            $('#div-1 .card').addClass('collapsed-card');
            $('#div-1 .card .card-body').css("display", "none")
            $('#aCollapse i').removeClass('fa-minus');
            $('#aCollapse i').addClass('fa-plus');
            $('button i.fas').removeClass('fa-minus');
            $('button i.fas').addClass('fa-plus');
        }

        function developperTout() {
            $('#div-1 .card').removeClass('collapsed-card');
            $('#div-1 .card .card-body').css("display", "block")
            $('#aCollapse i').removeClass('fa-plus');
            $('#aCollapse i').addClass('fa-minus');
            $('button i.fas').removeClass('fa-plus');
            $('button i.fas').addClass('fa-minus');
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
            objTable.find('th').wrapInner('<td />').contents().unwrap();           
            var thead = objTable.find("thead");
            var thRows = objTable.find("tr:first");
            var copy = thRows.clone(true).appendTo("thead");
            thRows.remove();            
            objTable.find('thead tr td').wrapInner('<th />').contents().unwrap().addClass('thead-dark');           
            objTable.find('tfoot').append("<tr></tr>");           
            objTable.find('tbody tr:first td').each(function () {
                objTable.find('tfoot tr').append("<td>&nbsp;</td>");
            });
            return false;
        }