
declare default element namespace 'http://www.oficinaRGB.pt/MakeReservation';
declare namespace o='http://www.oficinaRGB.pt/Office';


let $db := db:open("PEITP")//o:office

return
<office>
  {replace($db/o:reservations[o:date = "12-12-2021"]/o:slots/text(), '\d+', 'a')}
  {$db}
</office>
