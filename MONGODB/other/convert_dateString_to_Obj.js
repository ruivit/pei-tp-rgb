[{
    $addFields: {
        date_obj: {
            $dateFromString: {
                dateString: "$date",
                format: "%Y-%m-%d"
            }

        }
    }
}]
