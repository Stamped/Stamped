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
- (NSArray*)filteredCountryArrayForSection:(NSInteger)section;

@property (nonatomic, retain) NSDictionary* countryDictionary;
@property (nonatomic, retain) NSArray* countryCodeArray;
@property (nonatomic, retain) NSArray* indexArray;
@end

@implementation STSelectCountryViewController

@synthesize countryDictionary = countryDictionary_;
@synthesize countryCodeArray = countryCodeArray_;
@synthesize indexArray = indexArray_;

- (id)init {
  self = [super initWithNibName:@"STSelectCountryViewController" bundle:nil];
  if (self) {
    self.disableReload = YES;
    self.countryDictionary = [NSDictionary dictionaryWithObjectsAndKeys:
                              @"AFGHANISTAN", @"AF",
                              @"ÅLAND ISLANDS", @"AX",
                              @"ALBANIA", @"AL",
                              @"ALGERIA", @"DZ",
                              @"AMERICAN SAMOA", @"AS",
                              @"ANDORRA", @"AD",
                              @"ANGOLA", @"AO",
                              @"ANGUILLA", @"AI",
                              @"ANTARCTICA", @"AQ",
                              @"ANTIGUA AND BARBUDA", @"AG",
                              @"ARGENTINA", @"AR",
                              @"ARMENIA", @"AM",
                              @"ARUBA", @"AW",
                              @"AUSTRALIA", @"AU",
                              @"AUSTRIA", @"AT",
                              @"AZERBAIJAN", @"AZ",
                              @"BAHAMAS", @"BS",
                              @"BAHRAIN", @"BH",
                              @"BANGLADESH", @"BD",
                              @"BARBADOS", @"BB",
                              @"BELARUS", @"BY",
                              @"BELGIUM", @"BE",
                              @"BELIZE", @"BZ",
                              @"BENIN", @"BJ",
                              @"BERMUDA", @"BM",
                              @"BHUTAN", @"BT",
                              @"BOLIVIA, PLURINATIONAL STATE OF", @"BO",
                              @"BONAIRE, SINT EUSTATIUS AND SABA", @"BQ",
                              @"BOSNIA AND HERZEGOVINA", @"BA",
                              @"BOTSWANA", @"BW",
                              @"BOUVET ISLAND", @"BV",
                              @"BRAZIL", @"BR",
                              @"BRITISH INDIAN OCEAN TERRITORY", @"IO",
                              @"BRUNEI DARUSSALAM", @"BN",
                              @"BULGARIA", @"BG",
                              @"BURKINA FASO", @"BF",
                              @"BURUNDI", @"BI",
                              @"CAMBODIA", @"KH",
                              @"CAMEROON", @"CM",
                              @"CANADA", @"CA",
                              @"CAPE VERDE", @"CV",
                              @"CAYMAN ISLANDS", @"KY",
                              @"CENTRAL AFRICAN REPUBLIC", @"CF",
                              @"CHAD", @"TD",
                              @"CHILE", @"CL",
                              @"CHINA", @"CN",
                              @"CHRISTMAS ISLAND", @"CX",
                              @"COCOS (KEELING) ISLANDS", @"CC",
                              @"COLOMBIA", @"CO",
                              @"COMOROS", @"KM",
                              @"CONGO", @"CG",
                              @"CONGO, THE DEMOCRATIC REPUBLIC OF THE", @"CD",
                              @"COOK ISLANDS", @"CK",
                              @"COSTA RICA", @"CR",
                              @"CÔTE D'IVOIRE", @"CI",
                              @"CROATIA", @"HR",
                              @"CUBA", @"CU",
                              @"CURAÇAO", @"CW",
                              @"CYPRUS", @"CY",
                              @"CZECH REPUBLIC", @"CZ",
                              @"DENMARK", @"DK",
                              @"DJIBOUTI", @"DJ",
                              @"DOMINICA", @"DM",
                              @"DOMINICAN REPUBLIC", @"DO",
                              @"ECUADOR", @"EC",
                              @"EGYPT", @"EG",
                              @"EL SALVADOR", @"SV",
                              @"EQUATORIAL GUINEA", @"GQ",
                              @"ERITREA", @"ER",
                              @"ESTONIA", @"EE",
                              @"ETHIOPIA", @"ET",
                              @"FALKLAND ISLANDS (MALVINAS)", @"FK",
                              @"FAROE ISLANDS", @"FO",
                              @"FIJI", @"FJ",
                              @"FINLAND", @"FI",
                              @"FRANCE", @"FR",
                              @"FRENCH GUIANA", @"GF",
                              @"FRENCH POLYNESIA", @"PF",
                              @"FRENCH SOUTHERN TERRITORIES", @"TF",
                              @"GABON", @"GA",
                              @"GAMBIA", @"GM",
                              @"GEORGIA", @"GE",
                              @"GERMANY", @"DE",
                              @"GHANA", @"GH",
                              @"GIBRALTAR", @"GI",
                              @"GREECE", @"GR",
                              @"GREENLAND", @"GL",
                              @"GRENADA", @"GD",
                              @"GUADELOUPE", @"GP",
                              @"GUAM", @"GU",
                              @"GUATEMALA", @"GT",
                              @"GUERNSEY", @"GG",
                              @"GUINEA", @"GN",
                              @"GUINEA-BISSAU", @"GW",
                              @"GUYANA", @"GY",
                              @"HAITI", @"HT",
                              @"HEARD ISLAND AND MCDONALD ISLANDS", @"HM",
                              @"HOLY SEE (VATICAN CITY STATE)", @"VA",
                              @"HONDURAS", @"HN",
                              @"HONG KONG", @"HK",
                              @"HUNGARY", @"HU",
                              @"ICELAND", @"IS",
                              @"INDIA", @"IN",
                              @"INDONESIA", @"ID",
                              @"IRAN, ISLAMIC REPUBLIC OF", @"IR",
                              @"IRAQ", @"IQ",
                              @"IRELAND", @"IE",
                              @"ISLE OF MAN", @"IM",
                              @"ISRAEL", @"IL",
                              @"ITALY", @"IT",
                              @"JAMAICA", @"JM",
                              @"JAPAN", @"JP",
                              @"JERSEY", @"JE",
                              @"JORDAN", @"JO",
                              @"KAZAKHSTAN", @"KZ",
                              @"KENYA", @"KE",
                              @"KIRIBATI", @"KI",
                              @"KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF", @"KP",
                              @"KOREA, REPUBLIC OF", @"KR",
                              @"KUWAIT", @"KW",
                              @"KYRGYZSTAN", @"KG",
                              @"LAO PEOPLE'S DEMOCRATIC REPUBLIC", @"LA",
                              @"LATVIA", @"LV",
                              @"LEBANON", @"LB",
                              @"LESOTHO", @"LS",
                              @"LIBERIA", @"LR",
                              @"LIBYA", @"LY",
                              @"LIECHTENSTEIN", @"LI",
                              @"LITHUANIA", @"LT",
                              @"LUXEMBOURG", @"LU",
                              @"MACAO", @"MO",
                              @"MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF", @"MK",
                              @"MADAGASCAR", @"MG",
                              @"MALAWI", @"MW",
                              @"MALAYSIA", @"MY",
                              @"MALDIVES", @"MV",
                              @"MALI", @"ML",
                              @"MALTA", @"MT",
                              @"MARSHALL ISLANDS", @"MH",
                              @"MARTINIQUE", @"MQ",
                              @"MAURITANIA", @"MR",
                              @"MAURITIUS", @"MU",
                              @"MAYOTTE", @"YT",
                              @"MEXICO", @"MX",
                              @"MICRONESIA, FEDERATED STATES OF", @"FM",
                              @"MOLDOVA, REPUBLIC OF", @"MD",
                              @"MONACO", @"MC",
                              @"MONGOLIA", @"MN",
                              @"MONTENEGRO", @"ME",
                              @"MONTSERRAT", @"MS",
                              @"MOROCCO", @"MA",
                              @"MOZAMBIQUE", @"MZ",
                              @"MYANMAR", @"MM",
                              @"NAMIBIA", @"NA",
                              @"NAURU", @"NR",
                              @"NEPAL", @"NP",
                              @"NETHERLANDS", @"NL",
                              @"NEW CALEDONIA", @"NC",
                              @"NEW ZEALAND", @"NZ",
                              @"NICARAGUA", @"NI",
                              @"NIGER", @"NE",
                              @"NIGERIA", @"NG",
                              @"NIUE", @"NU",
                              @"NORFOLK ISLAND", @"NF",
                              @"NORTHERN MARIANA ISLANDS", @"MP",
                              @"NORWAY", @"NO",
                              @"OMAN", @"OM",
                              @"PAKISTAN", @"PK",
                              @"PALAU", @"PW",
                              @"PALESTINIAN TERRITORY, OCCUPIED", @"PS",
                              @"PANAMA", @"PA",
                              @"PAPUA NEW GUINEA", @"PG",
                              @"PARAGUAY", @"PY",
                              @"PERU", @"PE",
                              @"PHILIPPINES", @"PH",
                              @"PITCAIRN", @"PN",
                              @"POLAND", @"PL",
                              @"PORTUGAL", @"PT",
                              @"PUERTO RICO", @"PR",
                              @"QATAR", @"QA",
                              @"RÉUNION", @"RE",
                              @"ROMANIA", @"RO",
                              @"RUSSIAN FEDERATION", @"RU",
                              @"RWANDA", @"RW",
                              @"SAINT BARTHÉLEMY", @"BL",
                              @"SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA", @"SH",
                              @"SAINT KITTS AND NEVIS", @"KN",
                              @"SAINT LUCIA", @"LC",
                              @"SAINT MARTIN (FRENCH PART)", @"MF",
                              @"SAINT PIERRE AND MIQUELON", @"PM",
                              @"SAINT VINCENT AND THE GRENADINES", @"VC",
                              @"SAMOA", @"WS",
                              @"SAN MARINO", @"SM",
                              @"SAO TOME AND PRINCIPE", @"ST",
                              @"SAUDI ARABIA", @"SA",
                              @"SENEGAL", @"SN",
                              @"SERBIA", @"RS",
                              @"SEYCHELLES", @"SC",
                              @"SIERRA LEONE", @"SL",
                              @"SINGAPORE", @"SG",
                              @"SINT MAARTEN (DUTCH PART)", @"SX",
                              @"SLOVAKIA", @"SK",
                              @"SLOVENIA", @"SI",
                              @"SOLOMON ISLANDS", @"SB",
                              @"SOMALIA", @"SO",
                              @"SOUTH AFRICA", @"ZA",
                              @"SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS", @"GS",
                              @"SOUTH SUDAN", @"SS",
                              @"SPAIN", @"ES",
                              @"SRI LANKA", @"LK",
                              @"SUDAN", @"SD",
                              @"SURINAME", @"SR",
                              @"SVALBARD AND JAN MAYEN", @"SJ",
                              @"SWAZILAND", @"SZ",
                              @"SWEDEN", @"SE",
                              @"SWITZERLAND", @"CH",
                              @"SYRIAN ARAB REPUBLIC", @"SY",
                              @"TAIWAN, PROVINCE OF CHINA", @"TW",
                              @"TAJIKISTAN", @"TJ",
                              @"TANZANIA, UNITED REPUBLIC OF", @"TZ",
                              @"THAILAND", @"TH",
                              @"TIMOR-LESTE", @"TL",
                              @"TOGO", @"TG",
                              @"TOKELAU", @"TK",
                              @"TONGA", @"TO",
                              @"TRINIDAD AND TOBAGO", @"TT",
                              @"TUNISIA", @"TN",
                              @"TURKEY", @"TR",
                              @"TURKMENISTAN", @"TM",
                              @"TURKS AND CAICOS ISLANDS", @"TC",
                              @"TUVALU", @"TV",
                              @"UGANDA", @"UG",
                              @"UKRAINE", @"UA",
                              @"UNITED ARAB EMIRATES", @"AE",
                              @"UNITED KINGDOM", @"GB",
                              @"UNITED STATES", @"US",
                              @"UNITED STATES MINOR OUTLYING ISLANDS", @"UM",
                              @"URUGUAY", @"UY",
                              @"UZBEKISTAN", @"UZ",
                              @"VANUATU", @"VU",
                              @"VENEZUELA, BOLIVARIAN REPUBLIC OF", @"VE",
                              @"VIET NAM", @"VN",
                              @"VIRGIN ISLANDS, BRITISH", @"VG",
                              @"VIRGIN ISLANDS, U.S.", @"VI",
                              @"WALLIS AND FUTUNA", @"WF",
                              @"WESTERN SAHARA", @"EH",
                              @"YEMEN", @"YE",
                              @"ZAMBIA", @"ZM",
                              @"ZIMBABWE", @"ZW", nil];
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
  self.indexArray = [NSArray arrayWithObjects:@"A", @"B", @"C", @"D", @"E", @"F", @"G", @"H", @"I", @"J", @"K", @"L", 
     @"M", @"N", @"O", @"P", @"Q", @"R", @"S", @"T", @"U", @"V", @"W", @"X", @"Y", @"Z", nil];
  }
  return self;
}

- (void)dealloc {
  self.countryDictionary = nil;
  self.countryCodeArray = nil;
  self.indexArray = nil;
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

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITableViewDelegate methods.

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
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
  return cell;
}

#pragma mark - Private methods.

- (NSArray*)filteredCountryArrayForSection:(NSInteger)section {
  NSPredicate* predicate = [NSPredicate predicateWithFormat:@"SELF BEGINSWITH[cd] %@", [indexArray_ objectAtIndex:section]];
  NSArray* filtered = [countryDictionary_.allValues filteredArrayUsingPredicate:predicate];
  filtered = [filtered sortedArrayUsingSelector:@selector(localizedCaseInsensitiveCompare:)];
  return filtered;
}

@end
