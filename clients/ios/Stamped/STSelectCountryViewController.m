//
//  STSelectCountryViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 1/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSelectCountryViewController.h"

#import "STSelectCountryTableViewCell.h"

@interface STSelectCountryViewController ()
- (NSIndexPath*)indexPathForCountryCode:(NSString*)countryCode;
- (NSArray*)filteredCountryArrayForSection:(NSInteger)section;

@property (nonatomic, retain) NSArray* countryNameArray;
@property (nonatomic, retain) NSArray* countryCodeArray;
@property (nonatomic, retain) NSArray* indexArray;
@property (nonatomic, retain) NSIndexPath* selectedIndexPath;
@end

@implementation STSelectCountryViewController

@synthesize delegate = delegate_;
@synthesize countryNameArray = countryNameArray_;
@synthesize countryCodeArray = countryCodeArray_;
@synthesize indexArray = indexArray_;
@synthesize selectedIndexPath = selectedIndexPath_;

- (id)initWithCountryCode:(NSString*)countryCode {
  self = [super initWithNibName:@"STSelectCountryViewController" bundle:nil];
  if (self) {
    self.disableReload = YES;
    self.countryNameArray = [NSArray arrayWithObjects:
                             @"AFGHANISTAN",
                             @"ÅLAND ISLANDS",
                             @"ALBANIA",
                             @"ALGERIA",
                             @"AMERICAN SAMOA",
                             @"ANDORRA",
                             @"ANGOLA",
                             @"ANGUILLA",
                             @"ANTARCTICA",
                             @"ANTIGUA AND BARBUDA",
                             @"ARGENTINA",
                             @"ARMENIA",
                             @"ARUBA",
                             @"AUSTRALIA",
                             @"AUSTRIA",
                             @"AZERBAIJAN",
                             @"BAHAMAS",
                             @"BAHRAIN",
                             @"BANGLADESH",
                             @"BARBADOS",
                             @"BELARUS",
                             @"BELGIUM",
                             @"BELIZE",
                             @"BENIN",
                             @"BERMUDA",
                             @"BHUTAN",
                             @"BOLIVIA, PLURINATIONAL STATE OF",
                             @"BONAIRE, SINT EUSTATIUS AND SABA",
                             @"BOSNIA AND HERZEGOVINA",
                             @"BOTSWANA",
                             @"BOUVET ISLAND",
                             @"BRAZIL",
                             @"BRITISH INDIAN OCEAN TERRITORY",
                             @"BRUNEI DARUSSALAM",
                             @"BULGARIA",
                             @"BURKINA FASO",
                             @"BURUNDI",
                             @"CAMBODIA",
                             @"CAMEROON",
                             @"CANADA",
                             @"CAPE VERDE",
                             @"CAYMAN ISLANDS",
                             @"CENTRAL AFRICAN REPUBLIC",
                             @"CHAD",
                             @"CHILE",
                             @"CHINA",
                             @"CHRISTMAS ISLAND",
                             @"COCOS (KEELING) ISLANDS",
                             @"COLOMBIA",
                             @"COMOROS",
                             @"CONGO",
                             @"CONGO, THE DEMOCRATIC REPUBLIC OF THE",
                             @"COOK ISLANDS",
                             @"COSTA RICA",
                             @"CÔTE D'IVOIRE",
                             @"CROATIA",
                             @"CUBA",
                             @"CURAÇAO",
                             @"CYPRUS",
                             @"CZECH REPUBLIC",
                             @"DENMARK",
                             @"DJIBOUTI",
                             @"DOMINICA",
                             @"DOMINICAN REPUBLIC",
                             @"ECUADOR",
                             @"EGYPT",
                             @"EL SALVADOR",
                             @"EQUATORIAL GUINEA",
                             @"ERITREA",
                             @"ESTONIA",
                             @"ETHIOPIA",
                             @"FALKLAND ISLANDS (MALVINAS)",
                             @"FAROE ISLANDS",
                             @"FIJI",
                             @"FINLAND",
                             @"FRANCE",
                             @"FRENCH GUIANA",
                             @"FRENCH POLYNESIA",
                             @"FRENCH SOUTHERN TERRITORIES",
                             @"GABON",
                             @"GAMBIA",
                             @"GEORGIA",
                             @"GERMANY",
                             @"GHANA",
                             @"GIBRALTAR",
                             @"GREECE",
                             @"GREENLAND",
                             @"GRENADA",
                             @"GUADELOUPE",
                             @"GUAM",
                             @"GUATEMALA",
                             @"GUERNSEY",
                             @"GUINEA",
                             @"GUINEA-BISSAU",
                             @"GUYANA",
                             @"HAITI",
                             @"HEARD ISLAND AND MCDONALD ISLANDS",
                             @"HOLY SEE (VATICAN CITY STATE)",
                             @"HONDURAS",
                             @"HONG KONG",
                             @"HUNGARY",
                             @"ICELAND",
                             @"INDIA",
                             @"INDONESIA",
                             @"IRAN, ISLAMIC REPUBLIC OF",
                             @"IRAQ",
                             @"IRELAND",
                             @"ISLE OF MAN",
                             @"ISRAEL",
                             @"ITALY",
                             @"JAMAICA",
                             @"JAPAN",
                             @"JERSEY",
                             @"JORDAN",
                             @"KAZAKHSTAN",
                             @"KENYA",
                             @"KIRIBATI",
                             @"KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF",
                             @"KOREA, REPUBLIC OF",
                             @"KUWAIT",
                             @"KYRGYZSTAN",
                             @"LAO PEOPLE'S DEMOCRATIC REPUBLIC",
                             @"LATVIA",
                             @"LEBANON",
                             @"LESOTHO",
                             @"LIBERIA",
                             @"LIBYA",
                             @"LIECHTENSTEIN",
                             @"LITHUANIA",
                             @"LUXEMBOURG",
                             @"MACAO",
                             @"MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF",
                             @"MADAGASCAR",
                             @"MALAWI",
                             @"MALAYSIA",
                             @"MALDIVES",
                             @"MALI",
                             @"MALTA",
                             @"MARSHALL ISLANDS",
                             @"MARTINIQUE",
                             @"MAURITANIA",
                             @"MAURITIUS",
                             @"MAYOTTE",
                             @"MEXICO",
                             @"MICRONESIA, FEDERATED STATES OF",
                             @"MOLDOVA, REPUBLIC OF",
                             @"MONACO",
                             @"MONGOLIA",
                             @"MONTENEGRO",
                             @"MONTSERRAT",
                             @"MOROCCO",
                             @"MOZAMBIQUE",
                             @"MYANMAR",
                             @"NAMIBIA",
                             @"NAURU",
                             @"NEPAL",
                             @"NETHERLANDS",
                             @"NEW CALEDONIA",
                             @"NEW ZEALAND",
                             @"NICARAGUA",
                             @"NIGER",
                             @"NIGERIA",
                             @"NIUE",
                             @"NORFOLK ISLAND",
                             @"NORTHERN MARIANA ISLANDS",
                             @"NORWAY",
                             @"OMAN",
                             @"PAKISTAN",
                             @"PALAU",
                             @"PALESTINIAN TERRITORY, OCCUPIED",
                             @"PANAMA",
                             @"PAPUA NEW GUINEA",
                             @"PARAGUAY",
                             @"PERU",
                             @"PHILIPPINES",
                             @"PITCAIRN",
                             @"POLAND",
                             @"PORTUGAL",
                             @"PUERTO RICO",
                             @"QATAR",
                             @"RÉUNION",
                             @"ROMANIA",
                             @"RUSSIAN FEDERATION",
                             @"RWANDA",
                             @"SAINT BARTHÉLEMY",
                             @"SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA",
                             @"SAINT KITTS AND NEVIS",
                             @"SAINT LUCIA",
                             @"SAINT MARTIN (FRENCH PART)",
                             @"SAINT PIERRE AND MIQUELON",
                             @"SAINT VINCENT AND THE GRENADINES",
                             @"SAMOA",
                             @"SAN MARINO",
                             @"SAO TOME AND PRINCIPE",
                             @"SAUDI ARABIA",
                             @"SENEGAL",
                             @"SERBIA",
                             @"SEYCHELLES",
                             @"SIERRA LEONE",
                             @"SINGAPORE",
                             @"SINT MAARTEN (DUTCH PART)",
                             @"SLOVAKIA",
                             @"SLOVENIA",
                             @"SOLOMON ISLANDS",
                             @"SOMALIA",
                             @"SOUTH AFRICA",
                             @"SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS",
                             @"SOUTH SUDAN",
                             @"SPAIN",
                             @"SRI LANKA",
                             @"SUDAN",
                             @"SURINAME",
                             @"SVALBARD AND JAN MAYEN",
                             @"SWAZILAND",
                             @"SWEDEN",
                             @"SWITZERLAND",
                             @"SYRIAN ARAB REPUBLIC",
                             @"TAIWAN, PROVINCE OF CHINA",
                             @"TAJIKISTAN",
                             @"TANZANIA, UNITED REPUBLIC OF",
                             @"THAILAND",
                             @"TIMOR-LESTE",
                             @"TOGO",
                             @"TOKELAU",
                             @"TONGA",
                             @"TRINIDAD AND TOBAGO",
                             @"TUNISIA",
                             @"TURKEY",
                             @"TURKMENISTAN",
                             @"TURKS AND CAICOS ISLANDS",
                             @"TUVALU",
                             @"UGANDA",
                             @"UKRAINE",
                             @"UNITED ARAB EMIRATES",
                             @"UNITED KINGDOM",
                             @"UNITED STATES",
                             @"UNITED STATES MINOR OUTLYING ISLANDS",
                             @"URUGUAY",
                             @"UZBEKISTAN",
                             @"VANUATU",
                             @"VENEZUELA, BOLIVARIAN REPUBLIC OF",
                             @"VIET NAM",
                             @"VIRGIN ISLANDS, BRITISH",
                             @"VIRGIN ISLANDS, U.S.",
                             @"WALLIS AND FUTUNA",
                             @"WESTERN SAHARA",
                             @"YEMEN",
                             @"ZAMBIA",
                             @"ZIMBABWE", nil];
    self.countryCodeArray = [NSArray arrayWithObjects:
                             @"AF",
                             @"AX",
                             @"AL",
                             @"DZ",
                             @"AS",
                             @"AD",
                             @"AO",
                             @"AI",
                             @"AQ",
                             @"AG",
                             @"AR",
                             @"AM",
                             @"AW",
                             @"AU",
                             @"AT",
                             @"AZ",
                             @"BS",
                             @"BH",
                             @"BD",
                             @"BB",
                             @"BY",
                             @"BE",
                             @"BZ",
                             @"BJ",
                             @"BM",
                             @"BT",
                             @"BO",
                             @"BQ",
                             @"BA",
                             @"BW",
                             @"BV",
                             @"BR",
                             @"IO",
                             @"BN",
                             @"BG",
                             @"BF",
                             @"BI",
                             @"KH",
                             @"CM",
                             @"CA",
                             @"CV",
                             @"KY",
                             @"CF",
                             @"TD",
                             @"CL",
                             @"CN",
                             @"CX",
                             @"CC",
                             @"CO",
                             @"KM",
                             @"CG",
                             @"CD",
                             @"CK",
                             @"CR",
                             @"CI",
                             @"HR",
                             @"CU",
                             @"CW",
                             @"CY",
                             @"CZ",
                             @"DK",
                             @"DJ",
                             @"DM",
                             @"DO",
                             @"EC",
                             @"EG",
                             @"SV",
                             @"GQ",
                             @"ER",
                             @"EE",
                             @"ET",
                             @"FK",
                             @"FO",
                             @"FJ",
                             @"FI",
                             @"FR",
                             @"GF",
                             @"PF",
                             @"TF",
                             @"GA",
                             @"GM",
                             @"GE",
                             @"DE",
                             @"GH",
                             @"GI",
                             @"GR",
                             @"GL",
                             @"GD",
                             @"GP",
                             @"GU",
                             @"GT",
                             @"GG",
                             @"GN",
                             @"GW",
                             @"GY",
                             @"HT",
                             @"HM",
                             @"VA",
                             @"HN",
                             @"HK",
                             @"HU",
                             @"IS",
                             @"IN",
                             @"ID",
                             @"IR",
                             @"IQ",
                             @"IE",
                             @"IM",
                             @"IL",
                             @"IT",
                             @"JM",
                             @"JP",
                             @"JE",
                             @"JO",
                             @"KZ",
                             @"KE",
                             @"KI",
                             @"KP",
                             @"KR",
                             @"KW",
                             @"KG",
                             @"LA",
                             @"LV",
                             @"LB",
                             @"LS",
                             @"LR",
                             @"LY",
                             @"LI",
                             @"LT",
                             @"LU",
                             @"MO",
                             @"MK",
                             @"MG",
                             @"MW",
                             @"MY",
                             @"MV",
                             @"ML",
                             @"MT",
                             @"MH",
                             @"MQ",
                             @"MR",
                             @"MU",
                             @"YT",
                             @"MX",
                             @"FM",
                             @"MD",
                             @"MC",
                             @"MN",
                             @"ME",
                             @"MS",
                             @"MA",
                             @"MZ",
                             @"MM",
                             @"NA",
                             @"NR",
                             @"NP",
                             @"NL",
                             @"NC",
                             @"NZ",
                             @"NI",
                             @"NE",
                             @"NG",
                             @"NU",
                             @"NF",
                             @"MP",
                             @"NO",
                             @"OM",
                             @"PK",
                             @"PW",
                             @"PS",
                             @"PA",
                             @"PG",
                             @"PY",
                             @"PE",
                             @"PH",
                             @"PN",
                             @"PL",
                             @"PT",
                             @"PR",
                             @"QA",
                             @"RE",
                             @"RO",
                             @"RU",
                             @"RW",
                             @"BL",
                             @"SH",
                             @"KN",
                             @"LC",
                             @"MF",
                             @"PM",
                             @"VC",
                             @"WS",
                             @"SM",
                             @"ST",
                             @"SA",
                             @"SN",
                             @"RS",
                             @"SC",
                             @"SL",
                             @"SG",
                             @"SX",
                             @"SK",
                             @"SI",
                             @"SB",
                             @"SO",
                             @"ZA",
                             @"GS",
                             @"SS",
                             @"ES",
                             @"LK",
                             @"SD",
                             @"SR",
                             @"SJ",
                             @"SZ",
                             @"SE",
                             @"CH",
                             @"SY",
                             @"TW",
                             @"TJ",
                             @"TZ",
                             @"TH",
                             @"TL",
                             @"TG",
                             @"TK",
                             @"TO",
                             @"TT",
                             @"TN",
                             @"TR",
                             @"TM",
                             @"TC",
                             @"TV",
                             @"UG",
                             @"UA",
                             @"AE",
                             @"GB",
                             @"US",
                             @"UM",
                             @"UY",
                             @"UZ",
                             @"VU",
                             @"VE",
                             @"VN",
                             @"VG",
                             @"VI",
                             @"WF",
                             @"EH",
                             @"YE",
                             @"ZM",
                             @"ZW", nil];
  NSAssert(countryNameArray_.count == countryCodeArray_.count, @"Country name and code arrays must have the same number of objects");
  self.indexArray = [NSArray arrayWithObjects:@"A", @"B", @"C", @"D", @"E", @"F", @"G", @"H", @"I", @"J", @"K", @"L", 
     @"M", @"N", @"O", @"P", @"Q", @"R", @"S", @"T", @"U", @"V", @"W", @"X", @"Y", @"Z", nil];
  }

  self.selectedIndexPath = [self indexPathForCountryCode:countryCode];
  return self;
}

- (void)dealloc {
  self.countryNameArray = nil;
  self.countryCodeArray = nil;
  self.indexArray = nil;
  self.selectedIndexPath = nil;
  self.delegate = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
}

- (void)viewDidUnload {
  [super viewDidUnload];
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  if (selectedIndexPath_) {
    [self.tableView scrollToRowAtIndexPath:selectedIndexPath_
                          atScrollPosition:UITableViewScrollPositionMiddle
                                  animated:NO];
  }
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITableViewDelegate methods.

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
  self.selectedIndexPath = indexPath;
  for (STSelectCountryTableViewCell* cell in tableView.visibleCells) {
    cell.checked = ([[tableView indexPathForCell:cell] compare:indexPath] == NSOrderedSame);
    [cell setNeedsLayout];
  }
  NSString* country = [[self filteredCountryArrayForSection:indexPath.section] objectAtIndex:indexPath.row];
  NSString* code = [countryCodeArray_ objectAtIndex:[countryNameArray_ indexOfObject:country]];
  [delegate_ viewController:self didSelectCountry:country code:code];

  [tableView deselectRowAtIndexPath:indexPath animated:YES];
}

- (NSArray*)sectionIndexTitlesForTableView:(UITableView*)tableView {
  return indexArray_;
}

#pragma mark - UITableViewDataSource Methods.

- (NSInteger)numberOfSectionsInTableView:(UITableView*)tableView {
  return indexArray_.count;
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
  return [self filteredCountryArrayForSection:section].count;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath*)indexPath {
  NSArray* filtered = [self filteredCountryArrayForSection:indexPath.section];

  static NSString* CellIdentifier = @"Cell";
  STSelectCountryTableViewCell* cell = (STSelectCountryTableViewCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
  if (cell == nil) {
    cell = [[[STSelectCountryTableViewCell alloc] initWithReuseIdentifier:CellIdentifier] autorelease];
  }
  NSString* country = [filtered objectAtIndex:indexPath.row];
  cell.countryLabel.text = country.capitalizedString;
  if (selectedIndexPath_)
    cell.checked = ([selectedIndexPath_ compare:indexPath] == NSOrderedSame);
  return cell;
}

#pragma mark - Private methods.

- (NSIndexPath*)indexPathForCountryCode:(NSString*)countryCode {
  if (![countryCodeArray_ containsObject:countryCode])
    return nil;
  
  NSString* country = [countryNameArray_ objectAtIndex:[countryCodeArray_ indexOfObject:countryCode]];
  if (!country)
    return nil;

  NSPredicate* predicate = [NSPredicate predicateWithFormat:@"SELF BEGINSWITH[cd] %@", [country substringToIndex:1]];
  NSArray* filteredIndexes = [indexArray_ filteredArrayUsingPredicate:predicate];
  if (!filteredIndexes.count > 0)
    return nil;
  
  NSInteger section = [indexArray_ indexOfObject:filteredIndexes.lastObject];
  NSArray* filteredCountries = [self filteredCountryArrayForSection:section];
  NSInteger row = [filteredCountries indexOfObject:country];
  
  return [NSIndexPath indexPathForRow:row inSection:section];
}

- (NSArray*)filteredCountryArrayForSection:(NSInteger)section {
  NSPredicate* predicate = [NSPredicate predicateWithFormat:@"SELF BEGINSWITH[cd] %@", [indexArray_ objectAtIndex:section]];
  return [countryNameArray_ filteredArrayUsingPredicate:predicate];
}

@end
