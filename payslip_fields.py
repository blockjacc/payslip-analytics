from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class FieldCategory(str, Enum):
    AMOUNTS = "AMOUNTS"
    HOURS = "HOURS"
    TAXES = "TAXES"


@dataclass
class PayslipField:
    """Represents a payslip field with its database name, display alias, and category."""
    db_field: str
    display_name: str
    category: FieldCategory
    is_encrypted: bool = True


# Main data structure that holds all field mappings
PAYSLIP_FIELDS = {
    # AMOUNTS CATEGORY
    "basic_pay": PayslipField("basic_pay", "Base", FieldCategory.AMOUNTS),
    "regular_pay": PayslipField("regular_pay", "Regular", FieldCategory.AMOUNTS),
    "night_diff": PayslipField("night_diff", "Night Shift", FieldCategory.AMOUNTS),
    "overtime_pay": PayslipField("overtime_pay", "Overtime", FieldCategory.AMOUNTS),
    "sunday_holiday": PayslipField("sunday_holiday", "Holiday", FieldCategory.AMOUNTS),
    "allowances": PayslipField("allowances", "Tax Allow", FieldCategory.AMOUNTS),
    "nt_allowances": PayslipField("nt_allowances", "N-Tax Allow", FieldCategory.AMOUNTS),
    "hazard_pay": PayslipField("hazard_pay", "Hazard", FieldCategory.AMOUNTS),
    "cola": PayslipField("cola", "COLA", FieldCategory.AMOUNTS),
    "service_charge_taxable": PayslipField("service_charge_taxable", "Tax Service", FieldCategory.AMOUNTS),
    "service_charge_non_taxable": PayslipField("service_charge_non_taxable", "N-Tax Service", FieldCategory.AMOUNTS),
    "bonuses": PayslipField("bonuses", "Bonus", FieldCategory.AMOUNTS),
    "other_compensation": PayslipField("other_compensation", "Other", FieldCategory.AMOUNTS),
    "gross_pay": PayslipField("gross_pay", "Total", FieldCategory.AMOUNTS),
    "net_amount": PayslipField("net_amount", "Net", FieldCategory.AMOUNTS),
    "de_minimis": PayslipField("de_minimis", "De Minimis", FieldCategory.AMOUNTS),
    "leave_conversion_taxable": PayslipField("leave_conversion_taxable", "Tax Leave", FieldCategory.AMOUNTS),
    "leave_conversion_non_taxable": PayslipField("leave_conversion_non_taxable", "N-Tax Leave", FieldCategory.AMOUNTS),
    "paid_leave_amount": PayslipField("paid_leave_amount", "Paid Leave", FieldCategory.AMOUNTS),
    "retroactive_total_amount": PayslipField("retroactive_total_amount", "Retro", FieldCategory.AMOUNTS),
    "absences": PayslipField("absences", "Absences", FieldCategory.AMOUNTS),
    "employee_boost_amount": PayslipField("employee_boost_amount", "Boost", FieldCategory.AMOUNTS),
    "tardiness_pay": PayslipField("tardiness_pay", "Late", FieldCategory.AMOUNTS),
    "undertime_pay": PayslipField("undertime_pay", "Early", FieldCategory.AMOUNTS),
    "advance_amount": PayslipField("advance_amount", "Advance", FieldCategory.AMOUNTS),
    
    # HOURS CATEGORY
    "regular_days": PayslipField("regular_days", "Regular", FieldCategory.HOURS),
    "days_absent": PayslipField("days_absent", "Absent", FieldCategory.HOURS),
    "ot_no_hours": PayslipField("ot_no_hours", "Overtime", FieldCategory.HOURS),
    "retroactive_total_hours": PayslipField("retroactive_total_hours", "Retro", FieldCategory.HOURS),
    "employee_total_hours_service_charge_val": PayslipField("employee_total_hours_service_charge_val", "Service", FieldCategory.HOURS, False),
    
    # TAXES & DEDUCTIONS CATEGORY
    "pp_sss": PayslipField("pp_sss", "SSS", FieldCategory.TAXES),
    "pp_philhealth": PayslipField("pp_philhealth", "PHIC", FieldCategory.TAXES),
    "pp_pagibig": PayslipField("pp_pagibig", "HDMF", FieldCategory.TAXES),
    "pp_withholding_tax": PayslipField("pp_withholding_tax", "Tax", FieldCategory.TAXES),
    "pp_other_deductions": PayslipField("pp_other_deductions", "Other", FieldCategory.TAXES),
    "voluntary_contributions": PayslipField("voluntary_contributions", "Voluntary", FieldCategory.TAXES),
}


# Utility functions to work with the field mappings

def get_fields_by_category(category: FieldCategory) -> Dict[str, PayslipField]:
    """Returns all fields belonging to a specific category."""
    return {k: v for k, v in PAYSLIP_FIELDS.items() if v.category == category}


def get_amount_fields() -> Dict[str, PayslipField]:
    """Returns all fields in the AMOUNTS category."""
    return get_fields_by_category(FieldCategory.AMOUNTS)


def get_hour_fields() -> Dict[str, PayslipField]:
    """Returns all fields in the HOURS category."""
    return get_fields_by_category(FieldCategory.HOURS)


def get_tax_fields() -> Dict[str, PayslipField]:
    """Returns all fields in the TAXES category."""
    return get_fields_by_category(FieldCategory.TAXES)


def get_field_display_names_by_category(category: FieldCategory) -> Dict[str, str]:
    """Returns a mapping of field keys to their display names for a category."""
    fields = get_fields_by_category(category)
    return {k: v.display_name for k, v in fields.items()}


def get_all_field_display_names() -> Dict[str, str]:
    """Returns a mapping of all field keys to their display names."""
    return {k: v.display_name for k, v in PAYSLIP_FIELDS.items()} 