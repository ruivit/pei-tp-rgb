(: ============= Namespace Declarations ============= :)
module namespace page = 'http://basex.org/examples/web-page';
declare default element namespace 'http://www.oficinaRGB.pt/Reservation';
declare namespace o='http://www.oficinaRGB.pt/Office';
declare namespace f='http://www.oficinaRGB.pt/Family';

(: ============= Webpage ============= :)
declare
  %rest:GET
  %rest:path('')
  %output:method('xhtml')
  %output:omit-xml-declaration('no')
  %output:doctype-public('-//W3C//DTD XHTML 1.0 Transitional//EN')
  %output:doctype-system('http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd')
function page:start(
) as element(Q{http://www.w3.org/1999/xhtml}html) {
  <html xmlns='http://www.w3.org/1999/xhtml'>
    <head>
      <title>Welcome to [RGB API]</title>
      <link rel='stylesheet' type='text/css' href='static/style.css'/>
    </head>
    <body>
      <h1>[RGB API]</h1>
    </body>
  </html>
};


(: ============= POST XML ============= :)
declare %updating
  %rest:path("/makereservation")
  %rest:POST("{$xml}")
  %rest:consumes('application/xml')
  %rest:produces('application/xml')
function page:post-xml($xml)
{
  (: Check XML vs XSD :)
  let $xsd:= "XSD/Reservation.xsd"
  return validate:xsd($xml, $xsd),

  (: Make all the necessary checks
  if all checks are passed, write to DB :)
  page:checks($xml)
};

(: ============= Checks ============= :)
declare %updating function page:checks($xml)
{
  let $db := db:open("PEITP")
  let $pfd := $xml//f:preferedDates/text()
  let $nvdate := $xml//f:preferedDates[1]
  let $od := $db//o:date/text()
  
  (:filter the dates that the family choose and the available in the office :)
  where some $pfd in $od satisfies $pfd=$od
  
  (: check if the dates that the family choose are available, with availability of slots :)
  let $date := $db//o:reservations[o:date = $pfd][1]/o:date/text()
  let $slots := $db//o:reservations[o:date = $pfd and o:slots > 0][1]/o:date/text()
  
  (: set the reservationID to +1 since this might be a reservation :)
  let $rid := count($db//reservation/@reservationID) + 1
  
  (: if the date does not exist, create it and make the reservation :)
  return if (empty($date))
  then (
    db:replace("PEITP", "office1.xml", page:new-date($nvdate)),
    db:add("PEITP", page:valid-dates($xml, $nvdate), concat("reservation", count(db:open("PEITP")//reservation) + 1))
       )
      
  (: if there are no slots available, throw an error; else, make a reservation :)
  else (if (empty($slots))
       then (web:error(500, "[FALHA] Atingido o limite diário de reservas [FALHA]"))
       else (
    db:add("PEITP", page:valid-dates($xml, $nvdate), concat("reservation", count(db:open("PEITP")//reservation) + 1))),
    replace value of node $db//o:reservations[o:date = $date]/o:slots with $db//o:reservations[o:date = $date]/o:slots - 1
        )
};

(: return a valid xml of the new office date :)
declare function page:new-date($nvdate)
{
  let $db := db:open("PEITP")//o:office
  
  return 
  <office xmlns="http://www.oficinaRGB.pt/Office" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.oficinaRGB.pt/Office ../XSD/Office.xsd">
  {$db//o:reservations}
 <reservations xmlns="http://www.oficinaRGB.pt/Office" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <date>{$nvdate[1]/text()}</date>
        <slots>49</slots>
  </reservations>
</office>
};

(: return a valid xml with the valid date, that will be used to make a reservation :)
declare function page:valid-dates($xml, $vdate)
{
  let $db := db:open("PEITP")
  let $pfd := $xml//f:preferedDates/text()
  let $od := $db//o:date/text()
  
  where some $pfd in $od satisfies $pfd=$od
  
  let $date := $db//o:reservations[o:date = $pfd][1]/o:date/text()
  let $slots := $db//o:reservations[o:date = $pfd and o:slots/o:availableSlots > 0][1]/o:date/text()
  let $rid := count($db//reservation/@reservationID) + 1
    
  return
  if (empty($date))
  then (
  <reservation reservationID="{$rid}">
    <date>{$vdate}</date>
    <state>Active</state>
    <family>
      {$xml//f:numberElements}
      {$xml//f:familyElement}
      {$xml//f:country}
    </family>
  </reservation>)
  else (
  <reservation reservationID="{$rid}">
    <date>{$date}</date>
    <state>Active</state>
    <family>
      {$xml//f:numberElements}
      {$xml//f:familyElement}
      {$xml//f:country}
    </family>
  </reservation>)
};



(: ================ Check Availability ================ :)
declare
  %rest:path("/availability")
  %rest:GET
  %rest:query-param("date", "{$getdate}")
function page:check-availability($getdate as xs:string)
{
  if ($getdate = "all")
  then (
    for $db in db:open("PEITP")//o:reservations
  
    let $od := $db//o:date/text()
    let $slots := $db//o:slots/text()
    
    return if ($slots = 0)
    then (concat("Nao existe disponibilidade para o dia ", $od))
    else (concat("Existe disponibilidade para ", $slots, " familias para o dia ", $od))
      )
  else
      (
    let $db := db:open("PEITP")//o:office
  
    let $check := $getdate = $db//o:date/text()
    let $slots := $db//o:reservations[o:date = $getdate]/o:slots/text()
    
    return if ($check)
    then (concat("Existe disponibilidade para ", $slots, " familias para o dia ", $getdate))
    else (concat("Existe disponibilidade para 50 familias no dia ", $getdate))
      )
  
  (: GET RESQUEST Examples :)
  (: /availability?date=all :)
  (: /availability?date=XX-XX-XXXX :)
};


(: ================ Cancel Reservation ================ :)
declare %updating
  %rest:path("/cancelreservation")
  %rest:query-param("id", "{$id}")
function page:cancel-reservation($id as xs:string)
{
  let $db := db:open("PEITP")
  (: replace the XML in the DB with the new generated in function
     just like we did on page:check-dates() and page:storeindb :)
  return replace value of node $db//reservation[@reservationID = $id]/state with "Canceled",
  update:output(page:canceledok($id))
};


(: ================ Mensages ================ :)
declare function page:canceledok($id) {
  (: return a message :)
  '[CANCELED] Reservation with code ' || $id ||' [CANCELED]'
};

declare function page:ok() {
  (: return a message :)
  '[VALID] Reservation accepted [VALID]'
};