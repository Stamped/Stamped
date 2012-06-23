//
//  STEntitySearchController.m
//  Stamped
//
//  Created by Landon Judkins on 4/17/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntitySearchController.h"
#import "EntityDetailViewController.h"
#import "STEntitySearchSection.h"
#import "STEntityAutoCompleteResult.h"
#import <CoreLocation/CoreLocation.h>
#import "STImageCache.h"
#import "STTableViewSectionHeader.h"
#import "CreateStampViewController.h"

#define kAddEntityCellTag 101

static const CGFloat _innerBorderHeight = 40;
static const CGFloat _offscreenCancelPadding = 5;

@interface STEntitySearchTableViewCell : UITableViewCell
@property(nonatomic,retain) UILabel *titleLabel;
@property(nonatomic,retain) UILabel *detailTitleLabel;
@property(nonatomic,retain) STCancellation *iconCancellation;
@property(nonatomic,retain) UIImageView *iconView;
- (void)setSearchResult:(id<STEntitySearchResult>)searchResult;
@end

@interface STEntitySearchController () <UITableViewDelegate, UITableViewDataSource, UITextFieldDelegate, CLLocationManagerDelegate>

@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readonly, retain) NSString* initialQuery;
@property (nonatomic, readonly, retain) NSMutableArray<STEntityAutoCompleteResult>* autoCompleteResults;
@property (nonatomic, retain) NSArray<STEntitySearchSection>* suggestedSections;
@property (nonatomic, retain) NSArray<STEntitySearchSection>* searchSections;
@property (nonatomic, retain) NSString* coordinates;
@property (nonatomic, retain) STCancellation *autoCompleteCancellation;
@property (nonatomic, retain) STCancellation *searchCancellation;
@property (nonatomic, retain) STCancellation *requestCancellation;
@property (nonatomic, assign) BOOL loading;
@property (nonatomic, retain) CLLocationManager *locationManager;

@end

@implementation STEntitySearchController

@synthesize category = _category;
@synthesize initialQuery = _initialQuery;
@synthesize suggestedSections = _suggestedSections;
@synthesize searchSections = _searchSections;
@synthesize autoCompleteResults = _autoCompleteResults;
@synthesize coordinates = _coordinates;
@synthesize autoCompleteCancellation = _autoCompleteCancellation;
@synthesize requestCancellation = _requestCancellation;
@synthesize searchCancellation = _searchCancellation;
@synthesize loading = _loading;
@synthesize locationManager=_locationManager;

- (id)initWithCategory:(NSString*)category andQuery:(NSString*)query {
    if (self = [super init]) {
        
        if (!category) {
            category = @"music";
        }
        self.title = [Util titleForCategory:category];
        _category = [category retain];
        _initialQuery = [query retain];
        _autoCompleteResults = (id)[[NSMutableArray alloc] init];
        
    }
    return self;
}

- (void)dealloc {
    [_category release];
    [_initialQuery release];
    [_searchSections release];
    [_suggestedSections release];
    [_autoCompleteResults release];
    [_coordinates release];
    [_requestCancellation cancel];
    [_requestCancellation release];
    [_autoCompleteCancellation cancel];
    [_autoCompleteCancellation release];
    _locationManager.delegate = nil;
    [_locationManager release];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.showsSearchBar = YES;
    
    /*
    STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
    self.navigationItem.leftBarButtonItem = button;
    [button release];
    */
    BOOL loadResults = YES;
    CLLocation* location = [STStampedAPI sharedInstance].currentUserLocation;
    if ([_category isEqualToString:@"place"]) {
        _locationManager = [[CLLocationManager alloc] init];
        _locationManager.delegate = self; 
        _locationManager.desiredAccuracy = kCLLocationAccuracyBest; 
        _locationManager.distanceFilter = kCLDistanceFilterNone; 
        [_locationManager startUpdatingLocation];
        location = [_locationManager location];
        if (location) {
            [STStampedAPI sharedInstance].currentUserLocation = location;
            float longitude = location.coordinate.longitude;
            float latitude = location.coordinate.latitude;
            self.coordinates = [NSString stringWithFormat:@"%f,%f", latitude, longitude];
            [_locationManager stopUpdatingLocation];
        }
        else {
            loadResults = NO;
        }
    }
    if (loadResults) {
        [self reloadDataSource];
    }
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    self.tableView.contentOffset = CGPointZero;
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    self.tableView.contentOffset = CGPointZero;
}


#pragma mark - CLLocationManagerDelegate

- (void)locationManager:(CLLocationManager *)manager didUpdateToLocation:(CLLocation *)newLocation  fromLocation:(CLLocation *)oldLocation {
    
    float longitude = newLocation.coordinate.longitude;
    float latitude = newLocation.coordinate.latitude;
    self.coordinates = [NSString stringWithFormat:@"%f,%f", latitude, longitude];
    [STStampedAPI sharedInstance].currentUserLocation = newLocation;
    [_locationManager stopUpdatingLocation];
    if (!self.requestCancellation && !self.suggestedSections && !self.searchSections) {
        [self reloadDataSource];
    }
}

- (void)locationManager:(CLLocationManager *)manager didFailWithError:(NSError *)error {
    //[STStampedAPI sharedInstance].currentUserLocation = nil;
    [self reloadDataSource];
    [_locationManager stopUpdatingLocation];
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    
    [self dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (tableView == self.searchResultsTableView) {
        
        if (self.autoCompleteResults.count) {
            if (indexPath.row == self.autoCompleteResults.count) {
                return 62.0f;
            }
            return 47;
        }
        
    }
    
    
    
    return 64;
    
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    
    if (tableView == self.searchResultsTableView) {
        
        if (self.autoCompleteResults.count) {
            return self.autoCompleteResults.count;
        }
        
        if (self.searchSections) {
            id<STEntitySearchSection> sectionObject = [self.searchSections objectAtIndex:section];
            return sectionObject.entities.count; // + 1; // plus one to add 'add' cell
        }
        
        return 0; //1;
        
    }
    
    if (self.suggestedSections) {
        id<STEntitySearchSection> sectionObject = [self.suggestedSections objectAtIndex:section];
        return sectionObject.entities.count;
    }
    
    return 0;
    
    
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    
    if (tableView == self.searchResultsTableView) {
        
        if (self.autoCompleteResults.count) {
            return 1;
        }
        
        return self.searchSections ? self.searchSections.count : 0;
        
    }
    
    return self.suggestedSections ? self.suggestedSections.count : 0;
    
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if (tableView == self.searchResultsTableView && !self.autoCompleteResults.count) {
        NSInteger count = 0;
        if (self.searchSections) {
            id<STEntitySearchSection> sectionObject = [self.searchSections objectAtIndex:indexPath.section];
            count = sectionObject.entities.count;
        }
        
        if (indexPath.row == count) {
            static NSString *AddCellIdentifier = @"AddCellIdentfier";
            UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:AddCellIdentifier];
            if (cell == nil) {
                cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleSubtitle reuseIdentifier:AddCellIdentifier] autorelease];
                cell.tag = kAddEntityCellTag;
                cell.textLabel.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
                cell.detailTextLabel.textColor = [UIColor colorWithWhite:0.749f alpha:1.0f];
            }
            
            cell.indentationWidth = 4.0f;
            cell.indentationLevel = 9;
            cell.textLabel.text = @"Not found?";
            cell.detailTextLabel.text = [NSString stringWithFormat:@"add the %@ \"%@\"", self.category, [self.searchView text]];
            
            return cell;
        }
        
    }
    
    
    if (tableView == self.searchResultsTableView && self.autoCompleteResults.count) {
        id<STEntityAutoCompleteResult> autoCompleteResult = [self.autoCompleteResults objectAtIndex:indexPath.row];
        static NSString* reuseIdentifier = @"AutoCompleteIdentifier";
        UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:reuseIdentifier];
        if (!cell) {
            cell = [[[UITableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier] autorelease];
        }
        
        cell.textLabel.font = [UIFont stampedBoldFontWithSize:16];
        cell.textLabel.textColor = [UIColor stampedBlackColor];
        cell.textLabel.text = autoCompleteResult.completion;
        cell.indentationWidth = 4.0f;
        cell.indentationLevel = 9;
        
        return cell;
    }
    
    static NSString *CellIdentifier = @"CellIdentifier";
    STEntitySearchTableViewCell* cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (!cell) {
        cell = [[[STEntitySearchTableViewCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
    }
    
    id<STEntitySearchResult> result = nil;
    
    if (tableView == self.searchResultsTableView) {
        
        if (self.searchSections) {
            id<STEntitySearchSection> section = [self.searchSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        }
        
    } else {
        
        if (self.suggestedSections) {
            id<STEntitySearchSection> section = [self.suggestedSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        }
        
    }
    
    cell.searchResult = result;
    return cell;
    
}

- (NSString *)tableView:(UITableView *)tableView titleForHeaderInSection:(NSInteger)section {
    
    if (tableView == self.searchResultsTableView) {
        if (self.searchSections) {
            id<STEntitySearchSection> sectionObject = [self.searchSections objectAtIndex:section];
            return sectionObject.title;
        }
        return @"Search results";
    }
    
    if (self.suggestedSections) {
        id<STEntitySearchSection> sectionObject = [self.suggestedSections objectAtIndex:section];
        return sectionObject.title;
    }
    return nil;
    
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    if (![self tableView:tableView titleForHeaderInSection:section]) {
        return 0.0f;
    }
    return [STTableViewSectionHeader height];
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    NSString *title = [self tableView:tableView titleForHeaderInSection:section];
    if (title) {
        STTableViewSectionHeader *view = [[STTableViewSectionHeader alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, 0)];
        view.titleLabel.text = title;
        return [view autorelease];
    }
    return nil;
    
}


#pragma mark - UITableViewDelegate

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    
    
    if (tableView == self.searchResultsTableView) {
        
#warning this should take the user to create entity, not implemented yet
        NSInteger count = 0;
        if (self.autoCompleteResults.count) {
            count = self.autoCompleteResults.count;
        } else if (self.searchSections && indexPath.section < self.searchSections.count) {
            id<STEntitySearchSection> sectionObject = [self.searchSections objectAtIndex:indexPath.section];
            count = sectionObject.entities.count;
        }
        if (indexPath.row == count) {
            [tableView deselectRowAtIndexPath:indexPath animated:YES];
        }
        
    }
    
    if (self.autoCompleteResults.count) {
        
        if (self.autoCompleteResults.count > indexPath.row) {
            id<STEntityAutoCompleteResult> autoCompleteResult = [self.autoCompleteResults objectAtIndex:indexPath.row];
            [self.searchView setText:autoCompleteResult.completion];
            [self.searchView resignKeyboard];
            [self performSearchWithText:autoCompleteResult.completion];
        }
        else {
#warning former crasher, needs fix
        }
        /*
        id<STEntityAutoCompleteResult> autoCompleteResult = [self.autoCompleteResults objectAtIndex:indexPath.row];
        [self.searchView setText:autoCompleteResult.completion];
        [self.searchView resignKeyboard];
        [self performSearchWithText:autoCompleteResult.completion];
         */
    } else {
        
        id<STEntitySearchResult> result = nil;
        
        if (tableView == self.searchResultsTableView && self.searchSections) {
            id<STEntitySearchSection> section = [self.searchSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        } else if (self.suggestedSections) {
            id<STEntitySearchSection> section = [self.suggestedSections objectAtIndex:indexPath.section];
            result = [section.entities objectAtIndex:indexPath.row];
        }
        
        CreateStampViewController *controller = [[CreateStampViewController alloc] initWithSearchResult:result];
        [self.navigationController pushViewController:controller animated:YES];
        [controller release];
        
    }
    
}


#pragma mark STSearchViewDelegate

- (void)performSearchWithText:(NSString*)text {
    
    [self.searchCancellation cancel];
    self.searchCancellation = nil;
    [self.autoCompleteCancellation cancel];
    self.autoCompleteCancellation = nil;
    [self.autoCompleteResults removeAllObjects];
    [self.searchResultsTableView reloadData];
    [self.searchView setLoading:YES];
    
    STEntitySearch *search = [[[STEntitySearch alloc] init] autorelease];
    search.category = self.category;
    search.query = text;
    search.coordinates = self.coordinates;
    self.searchCancellation = [[STStampedAPI sharedInstance] entityResultsForEntitySearch:search andCallback:^(NSArray<STEntitySearchSection> *sections, NSError *error, STCancellation* cancellation) {
        
        [self.searchView setLoading:NO];
        self.searchCancellation = nil;
        if (sections) {
            self.searchSections = sections;
            [self.searchResultsTableView reloadData];
        }
        
    }];
    
}

- (void)stSearchViewHitSearch:(STSearchView*)view withText:(NSString*)text {
    
    [self performSearchWithText:text];
    
}

- (void)stSearchView:(STSearchView*)view textDidChange:(NSString*)text {
    
    [super stSearchView:view textDidChange:text];
    [self.autoCompleteCancellation cancel];
    self.autoCompleteCancellation = nil;
    
    if (!text || [text stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]].length <= 1) {
        return;
    }
    
    [self.searchView setLoading:YES];
    self.autoCompleteCancellation = [[STStampedAPI sharedInstance] entityAutocompleteResultsForQuery:text coordinates:self.coordinates category:self.category andCallback:^(NSArray<STEntityAutoCompleteResult> *results, NSError *error, STCancellation *cancellation) {
        
        self.autoCompleteCancellation = nil;
        [self.autoCompleteResults removeAllObjects];
        if (results.count) {
            [self.autoCompleteResults addObjectsFromArray:results];
        }
        [self.searchResultsTableView reloadData];
        [self.searchView setLoading:NO];
        
    }];
    
    UITableViewCell *cell = (UITableViewCell*)[self.searchResultsTableView viewWithTag:kAddEntityCellTag];
    if (cell) {
        [cell.detailTextLabel setText:[NSString stringWithFormat:@"add the %@ \"%@\"", self.category, text]];
    }
    
}

- (void)stSearchViewDidCancel:(STSearchView*)view {
    [super stSearchViewDidCancel:view];
    
    [self.searchCancellation cancel];
    self.searchCancellation = nil;
    [self.autoCompleteCancellation cancel];
    self.autoCompleteCancellation = nil;
    
}


#pragma mark - STRestController

- (BOOL)dataSourceReloading {
    return _loading;
}

- (void)loadNextPage {
}

- (BOOL)dataSourceHasMoreData {
    return NO;
}

- (void)reloadDataSource {
    if (_loading) return; 
    _loading = YES;
    
    STEntitySuggested* suggested = [[[STEntitySuggested alloc] init] autorelease];
    suggested.coordinates = self.coordinates;
    suggested.category = self.category;
    
    self.requestCancellation = [[STStampedAPI sharedInstance] entityResultsForEntitySuggested:suggested  andCallback:^(NSArray<STEntitySearchSection> *results, NSError *error, STCancellation* cancellation) {
        
        NSInteger sections = [self.tableView numberOfSections];
        self.requestCancellation = nil;
        if (results) {
            self.suggestedSections = results;
            
            if (sections == 0 && self.suggestedSections) {
                
                [self.tableView beginUpdates];
                [self.tableView insertSections:[NSIndexSet indexSetWithIndexesInRange:NSMakeRange(0, self.suggestedSections.count)] withRowAnimation:UITableViewRowAnimationFade];
                [self.tableView endUpdates];
                
            } else {
                
                [self.tableView reloadData];

            }
            
        }
        
        _loading = NO;
        [self dataSourceDidFinishLoading];
        if (sections==0) {
            //[self animateIn];
        }
        
    }];
    [super reloadDataSource];
    
}

- (BOOL)dataSourceIsEmpty {
    return (self.suggestedSections.count==0);
}

- (void)setupNoDataView:(NoDataView*)view {
    
    CGRect frame = view.frame;
    CGFloat height = self.tableView.tableHeaderView.bounds.size.height;
    frame.origin.y = height;
    frame.size.height -= height;
    view.frame = frame;
    [view setupWithTitle:@"No Suggestions" detailTitle:@"No suggestions found."];
    
}

@end


#pragma mark - STEntitySearchTableViewCell

@implementation STEntitySearchTableViewCell

@synthesize titleLabel = _titleLabel;
@synthesize detailTitleLabel = _detailTitleLabel;
@synthesize iconCancellation = _iconCancellation;
@synthesize iconView = _iconView;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier])) {
        
        UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(12, 17, 16, 16)];
        imageView.contentMode = UIViewContentModeScaleAspectFit;
        [self.contentView addSubview:imageView];
        _iconView = [imageView retain];
        [imageView release];
        
        UIFont *font = [UIFont stampedTitleFontWithSize:24];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(36.0f, 12.0f, 0.0f, font.lineHeight)];
        label.textColor = [UIColor stampedBlackColor];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor whiteColor];
        [self addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        font = [UIFont stampedFontWithSize:12];
        label = [[UILabel alloc] initWithFrame:CGRectMake(36.0f, CGRectGetMaxY(_titleLabel.frame)-2.0f, 0.0f, font.lineHeight)];
        label.textColor = [UIColor stampedGrayColor];
        label.highlightedTextColor = [UIColor whiteColor];
        label.font = font;
        label.backgroundColor = [UIColor whiteColor];
        [self addSubview:label];
        _detailTitleLabel = [label retain];
        [label release];
        
    }
    return self;
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [_titleLabel sizeToFit];
    [_detailTitleLabel sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width - 40.0f, frame.size.width);
    _titleLabel.frame = frame;
    
    frame = _detailTitleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width - 40.0f, frame.size.width);
    _detailTitleLabel.frame = frame;
    
}

- (void)dealloc {
    [_iconCancellation cancel];
    [_iconCancellation release];
    [_iconView release];
    [_detailTitleLabel release];
    [_titleLabel release];
    [super dealloc];
}

- (void)setSearchResult:(id<STEntitySearchResult>)searchResult {
    self.iconView.image = nil;
    
    _titleLabel.text = searchResult.title;
    _detailTitleLabel.text = searchResult.subtitle;
    
    [self.iconCancellation cancel];
    self.iconCancellation = nil;
    NSString* iconURL = searchResult.icon;
    if (iconURL) {
        
        UIImage *icon = [[STImageCache sharedInstance] cachedImageForImageURL:iconURL];
        if (icon) {
            dispatch_async(dispatch_get_main_queue(), ^{
                self.iconView.image = icon;
            });
        }
        else {
            self.iconCancellation = [[STImageCache sharedInstance] imageForImageURL:iconURL andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                if (image) {
                    self.iconView.image = image;
                }
                self.iconCancellation = nil;
            }];
        }
    }
    
}

@end


