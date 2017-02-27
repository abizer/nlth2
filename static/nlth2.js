function post_data()
{
	order_update();
	$.ajax({
		type: 'POST',
		url: '/add/transaction',
		data: { 
			'items': [x], 
			'name': $('input[name=cust_name]').val(),
		},
		traditional: true,
		dataType: 'json',
	}).done(function(data) 
		{
			update_transaction_list();
			$('.alert_field').text( data.message ); 
			$('#autoname').val('')
			$('.box:checked').each( function(index, element)
			{
				$(element).change().val(0).removeAttr('checked').parent().siblings().find('.quantity').val(1);
			});
			order_update();
		});
}

function update_transaction_list()
{
	var transaction_container = $('<div class="transaction_container"></div>');
	transaction_container.append('<p>' + $('#autoname').val() + ': ' + $('#total_cost').text() + '</p>');
	transaction_container.append($('<ul> </ul>'));
	for( var i = 0; i < x.length; i++ )
	{
		transaction_container.children('ul').append('<li>' + $('label[for=' + x[i] +']').text() + '</li>'); 
	}
	$('#transaction_list').append(transaction_container);
}

function order_update()
{
	x = [];
	cost = 0.0; 
	$('.box:checked').each( function(index, element)
	{
		m = $(element);
		for ( i = 0; i < m.parent().siblings().find('.quantity').val(); i++)
		{
			x.push(m.attr('data-id'));
			cost += parseFloat(m.attr('data-cost')); 
		}
	});

	cost_update();
}

function cost_update()
{
	$('#total_cost').text("$" + cost.toFixed(2));
	$('#change_5').text("$" + (5 - cost).toFixed(2));
	$('#change_10').text("$" + (10 - cost).toFixed(2));
	$('#change_20').text("$" + (20 - cost).toFixed(2));
}

function delete_transaction(tid)
{
	$.post(
		'/delete/transaction/' + tid
	).done(function(data) {
		console.log(data);
		$('.alert_field').text(data.message);
		$('tr[data-rowid='+tid+']').remove();
	});
}

var names = 
["Ayan Longhi", "Isa Eugenio", "Kaili Welch", "Kimia Faroughi", "Lauren Franklin",
"Pallavi Bollapragada", "Rania Ahnad", "Sonia Pramanick", "Sophia Flanigan", "William Leber", 
"Ananda Guha", "Dawson Wood",
"Gaurav Varma", "Habeeb Khajasha", "Haneef Khajasha", "Lauren Chang",
"Meghana Murty", "Siddhant Yawalker", "Tejas Raghuram", "Vanshika Sharma", "Vincent Huang",
"Aaron Chen", "Ananya Hindocha", "Andrei Volgin", "Blake Werner", "Jessica Anthony",
"Sachin Sharma", "Sophia Wagganer", "Timothy Yang", "Tyler Hertel", "Tyler Kariya",
"Abhinav Arora", "Ali Ashraf", "Alyssa Vessel", "Mark Emmons", "Tanvi Kaur",
"Vivek Hatte", "Amalia Barrett", "Anika Varma", "Darren Tong", "Olivia Waggonner",
"Vigna Kumar", "Vrinda Suresh", "Young Wang", "Alexandra Petersen", "Justin Tong",
"Kai Craig", "Meghna Agarwal", "Rhea Kerawala", "Rishabh Singhal", "Sarah Buzsaki",
"Abizer Lokhandwala", "Faith Rovetta", "Harmani Sethi", "Jessamyn Fathi", "Krti Tallam",
"Stevi Ibonie", "Mrs. Mimi", "Mr. Bill", 
"Ms. Jennifer", "Ms. Michelle", "Mrs. Buzsaki", "Mrs. Petersen" ].sort();
		
$( function() {
	$("#autoname").autocomplete({
			source: function( request, response ) {
            var matcher = new RegExp( "^" + $.ui.autocomplete.escapeRegex( request.term ), "i" );
            response( $.grep( names, function( item ){
                return matcher.test( item );
            }) );
        },
			delay: 0,
			autoFocus: true
		});

	$('ul.nav li a').filter(function() {
	    return this.href == window.location;
	}).parent().addClass('active');

	$('#input-rowid').attr('readonly', 'readonly');

	$( ".submit_transaction").click( function()
	{
		post_data();
	});

	$('.box, .quantity').change(
		function() {
			order_update(); 
		}
	);
});

