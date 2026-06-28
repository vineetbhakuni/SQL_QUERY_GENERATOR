from datetime import date
from typing import Optional

from sqlalchemy import CHAR, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Region(Base):
    __tablename__ = "regions"

    region_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_name: Mapped[Optional[str]] = mapped_column(String(25))

    countries: Mapped[list["Country"]] = relationship("Country", back_populates="region")


class Country(Base):
    __tablename__ = "countries"

    country_id: Mapped[str] = mapped_column(CHAR(2), primary_key=True)
    country_name: Mapped[Optional[str]] = mapped_column(String(40))
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.region_id"), nullable=False)

    region: Mapped["Region"] = relationship("Region", back_populates="countries")
    locations: Mapped[list["Location"]] = relationship("Location", back_populates="country")


class Location(Base):
    __tablename__ = "locations"

    location_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    street_address: Mapped[Optional[str]] = mapped_column(String(40))
    postal_code: Mapped[Optional[str]] = mapped_column(String(12))
    city: Mapped[str] = mapped_column(String(30), nullable=False)
    state_province: Mapped[Optional[str]] = mapped_column(String(25))
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.country_id"), nullable=False)

    country: Mapped["Country"] = relationship("Country", back_populates="locations")
    departments: Mapped[list["Department"]] = relationship("Department", back_populates="location")


class Job(Base):
    __tablename__ = "jobs"

    job_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_title: Mapped[str] = mapped_column(String(35), nullable=False)
    min_salary: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    max_salary: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))

    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="job")


class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_name: Mapped[str] = mapped_column(String(30), nullable=False)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.location_id"))

    location: Mapped[Optional["Location"]] = relationship("Location", back_populates="departments")
    employees: Mapped[list["Employee"]] = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(20))
    last_name: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.job_id"), nullable=False)
    salary: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.employee_id"))
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.department_id"))

    job: Mapped["Job"] = relationship("Job", back_populates="employees")
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="employees")
    dependents: Mapped[list["Dependent"]] = relationship("Dependent", back_populates="employee")


class Dependent(Base):
    __tablename__ = "dependents"

    dependent_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    # column name kept as "relationship" in DB; Python attr renamed to avoid shadowing sqlalchemy's relationship()
    relation_type: Mapped[str] = mapped_column("relationship", String(25), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"), nullable=False)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="dependents")
