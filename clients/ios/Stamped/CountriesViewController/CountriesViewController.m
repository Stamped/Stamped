//
//  CountriesViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/19/12.
//
//

#import "CountriesViewController.h"
#import "STTableViewSectionHeader.h"

#define kCellCheckMarkTag 301

@interface CountriesTableCell : UITableViewCell
@end

@interface CountriesViewController ()
@property(nonatomic,retain,readonly) NSArray *dataSource;
@property(nonatomic,retain,readonly) NSArray *sectionTitles;
@end

@implementation CountriesViewController
@synthesize dataSource=_dataSource;
@synthesize sectionTitles=_sectionTitles;
@synthesize selectedCountry;
@synthesize delegate;

- (void)commonInit {
    
    self.title = NSLocalizedString(@"Countries", @"Countries");
    
    NSMutableArray *countriesArray = [[NSMutableArray alloc] init];
    NSMutableArray *sectionTitlesArray = [[NSMutableArray alloc] init];

    NSLocale *locale = [[NSLocale alloc] initWithLocaleIdentifier:@"en_US"];
        
    NSArray *countryArray = [NSLocale ISOCountryCodes];
    
    for (NSString *countryCode in countryArray) {
        NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];
        [countriesArray addObject:[locale displayNameForKey:NSLocaleCountryCode value:countryCode]];
        [pool release];
    }
    
    [locale release];

    [countriesArray sortUsingSelector:@selector(compare:)];

    NSMutableArray *sectionsArray = [[NSMutableArray alloc] init];
    NSMutableArray *section = nil;

    for (NSString *country in countriesArray) {
        
        NSString *countryIndex = [[country substringToIndex:1] uppercaseString];
        
        if ([sectionTitlesArray count] == 0 || ![countryIndex isEqualToString:[sectionTitlesArray lastObject]]) {

            [sectionTitlesArray addObject:countryIndex];

            if (section!=nil) {
                [section sortUsingSelector:@selector(compare:)];
                [sectionsArray addObject:section];
                [section release], section=nil;
            }
            section = [[NSMutableArray alloc] init];
        }
        [section addObject:country];
        
    }
    
    [section release], section=nil;
    [countriesArray release];

    _sectionTitles = [sectionTitlesArray retain];
    [sectionTitlesArray release];
    
    _dataSource = [sectionsArray retain];
    [sectionsArray release];
    
}

- (id)initWithStyle:(UITableViewStyle)style {
    if (self = [super initWithStyle:style]) {
        [self commonInit];
    }
    return self;
}

- (id)init {
    return [self initWithStyle:UITableViewStylePlain];
}

- (void)dealloc {
    self.selectedCountry = nil;
    self.delegate = nil;
    [_sectionTitles release], _sectionTitles=nil;
    [_dataSource release], _dataSource=nil;
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
    self.navigationItem.leftBarButtonItem = button;
    [button release];
    
    button = [[STNavigationItem alloc] initWithTitle:@"Save" style:UIBarButtonItemStyleDone target:self action:@selector(save:)];
    self.navigationItem.rightBarButtonItem = button;
    [button release];
    
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
}


#pragma mark - Actions

- (void)save:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(contriesViewController:selectedCountry:)]) {
        [self.delegate contriesViewController:self selectedCountry:self.selectedCountry];
    }
    
}

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(contriesViewControllerCancelled:)]) {
        [self.delegate contriesViewControllerCancelled:self];
    }
    
}


#pragma mark - UITableViewDataSource

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    
    return [_dataSource count];
    
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return [(NSArray*)[_dataSource objectAtIndex:section] count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"Cell";
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
        cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.textLabel.font = [UIFont boldSystemFontOfSize:16];
    }
    
    cell.textLabel.text = [[_dataSource objectAtIndex:indexPath.section] objectAtIndex:indexPath.row];
    
    if ([cell.textLabel.text isEqualToString:self.selectedCountry]) {
        
        cell.indentationLevel = 2;
        cell.indentationWidth = 6;
        
        cell.imageView.image = [UIImage imageNamed:@"countries_cell_check.png"];
        cell.textLabel.textColor = [UIColor colorWithRed:0.215f green:0.478f blue:0.850f alpha:1.0f];
        
    } else {
        
        cell.indentationLevel = 6;
        cell.indentationWidth = 6;
        
        cell.imageView.image = nil;
        cell.textLabel.textColor = [UIColor colorWithWhite:0.149f alpha:1.0f];

    }
    
    return cell;
}

- (NSArray *)sectionIndexTitlesForTableView:(UITableView *)tableView {
    return _sectionTitles;
}


#pragma mark - UITableViewDelegate

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    
    return [_sectionTitles objectAtIndex:section];
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    return [STTableViewSectionHeader height];
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    NSString *title = [self tableView:tableView titleForHeaderInSection:section];
    STTableViewSectionHeader *view = [[STTableViewSectionHeader alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, 0)];
    view.titleLabel.text = title;
    return [view autorelease];
    
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
     
    
    UITableViewCell *cell = [tableView cellForRowAtIndexPath:indexPath];
    [self.tableView reloadData];
    [cell setSelected:YES];
    [tableView deselectRowAtIndexPath:indexPath animated:YES];
    
    if ([cell.textLabel.text isEqualToString:self.selectedCountry]) {
        cell.imageView.image = [UIImage imageNamed:@"countries_cell_check.png"];
    }
    
    self.selectedCountry = [[_dataSource objectAtIndex:indexPath.section] objectAtIndex:indexPath.row];
    
}

@end
