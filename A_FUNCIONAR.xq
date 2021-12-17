declare default element namespace 'http://www.oficinaRGB.pt/Family';
declare namespace o='http://www.oficinaRGB.pt/Office';

let $x := db:open("PEITP")

let $pd := $x//preferedDates/text()
let $od := $x//o:date/text()

where some $pd in $od satisfies $pd=$od

(: 
return for $dates in $x//preferedDates/text()
        where $dates = $od
        return if ($x//o:office[o:date = $dates]/o:slots/o:availableSlots > 0)
        then $dates
:)

return $x//o:office[o:date = $pd and o:slots/o:availableSlots > 0][1]/o:date/text()
        
        

      