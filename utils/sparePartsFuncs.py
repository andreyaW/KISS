def repairWithSpareParts(comp, spare_parts):
    """
    Repair a component using spare parts if available.
    """
    if spare_parts > 0:

        
        comp.repair()
        spare_parts -= 1
    if spare_parts ==0:
        
        print("No spare parts left.")
        # orderSpareParts()

    return spare_parts


def orderSpareParts():
    """
    Logic to order new spare parts.
    """
    # Placeholder for ordering logic
    print("Ordering new spare parts...")