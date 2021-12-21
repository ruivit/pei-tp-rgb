(: ============= Namespace Declarations ============= :)
module namespace page = 'http://basex.org/examples/web-page';
declare default element namespace 'http://www.oficinaRGB.pt/MakeReservation';
declare namespace r='http://www.oficinaRGB.pt/Reservations';
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
function page:check-xml($xml)
{
  (: Check XML vs XSD :)
  let $xsd:= "XSD/ReservationPOST.xsd"
  return validate:xsd($xml, $xsd),

  (: Try to insert into DB :)
  page:storeindb($xml),

  (: If no error occurs, go to function :)
  update:output(page:ok())
};

declare function page:ok() {
  (: return a message :)
  '[VALID] Reservation accepted [VALID]'
};


(: ============= Store in database ============= :)
declare %updating function page:storeindb($xml)
{
  db:add("PEITP", page:check-dates($xml), concat("reservation", count(db:open("PEITP")//reservation) + 1))
};

(: ============= Check Dates ============= :)
declare function page:check-dates($xml)
{
(: 
  pfd - Prefered Family Dates
  $od - Office Days (days available for reservation)
  $dates - the AVAILABLE DATES (result of the comparation)
:)

  let $db := db:open("PEITP")
  let $pfd := $xml//f:preferedDates/text()
  let $od := $db//o:date/text()
  
  (:filter the dates that the family choose and the available in the office :)
  where some $pfd in $od satisfies $pfd=$od
  
  (: check if the dates that the family choose are available, with availability of slots :)
  let $date := $db//o:office[o:date = $pfd and o:slots/o:availableSlots > 0][1]/o:date/text()
  
  (: set the reservationID to +1 since this might be a reservation :)
  let $rid := count($db//r:reservation/@reservationID) + 1
  
  (: return a valid XML that serves as an actual reservation :)
  return
  <reservation reservationID="{$rid}">
    <date>{$date}</date>
    <state>Active</state>
    <family>
      {$xml//f:numberElements}
      {$xml//f:familyElement}
      {$xml//f:country}
    </family>
  </reservation>
};


(: ================ Check Availability ================ :)
declare
  %rest:path("/availability")
  %rest:GET
  %rest:query-param("date", "{$date}")
function page:check-availability($date as xs:string)
{
  for $db in db:open("PEITP")//o:office
  
  let $od := $db//o:date/text()
  let $aS := $db//o:availableSlots/text()
  
  return 
  if ($date = "all")
  then ( concat($aS, " available slots for the date ", $od) )
  
  else if ($date = $od) 
  then (
    if ($aS = 0) 
    then ( concat("NO SLOTS AVAILABLE FOR DATE ", $date) )
    else ( concat($aS, " available slots for the date ", $od) )
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
  (: replace the XML in the DB with the new generated in function
     just like we did on page:check-dates() and page:storeindb :)
  db:replace("PEITP", concat("reservation", $id), page:canceledxml($id)),
  update:output(page:canceledok($id))
};

declare function page:canceledxml($id)
{
  let $db := db:open("PEITP")
  let $reservation := $db//r:reservation[@reservationID = $id]
  let $rid := $db//r:reservation[@reservationID = $id]/@reservationID

  return
  <reservation reservationID="{$rid}">
    <date>{$reservation//date/text()}</date>
    <state>Canceled</state>
    <family>
      {$db//f:numberElements}
      {$db//f:familyElement}
      {$db//f:country}
    </family>
  </reservation>
};
declare function page:canceledok($id) {
  (: return a message :)
  '[CANCELED] Reservation with code ' || $id ||' [CANCELED]'
};


