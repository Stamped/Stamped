//
//  STMusicViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STConsumptionViewController.h"
#import "STToolbarView.h"
#import "STGenericTableDelegate.h"
#import "STConsumptionLazyList.h"
#import "STFriendsSlice.h"
#import "STStampCellFactory.h"
#import "STCellStyles.h"
#import "Util.h"
#import <QuartzCore/QuartzCore.h>
#import "STButton.h"
#import "STScopeSlider.h"
#import "STStampedAPI.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STConfiguration.h"
#import "STConsumptionToolbarItem.h"
#import "STConsumptionToolbar.h"

//Film
static NSString* _movieNameKey = @"Consumption.film.movie.name";
static NSString* _movieIconKey = @"Consumption.film.movie.icon";
static NSString* _movieBackIconKey = @"Consumption.film.movie.backIcon";

static NSString* _inTheatersIconKey = @"Consumption.film.movie.inTheaters.icon";
static NSString* _inTheatersBackIconKey = @"Consumption.film.movie.inTheaters.backIcon";
static NSString* _inTheatersNameKey = @"Consumption.film.movie.inTheaters.name";
static NSString* _inTheatersFilterKey = @"Consumption.film.movie.inTheaters.filter";

static NSString* _onlineAndDVDIconKey = @"Consumption.film.movie.onlineAndDVD.icon";
static NSString* _onlineAndDVDBackIconKey = @"Consumption.film.movie.onlineAndDVD.backIcon";
static NSString* _onlineAndDVDNameKey = @"Consumption.film.movie.onlineAndDVD.name";
static NSString* _onlineAndDVDFilterKey = @"Consumption.film.movie.onlineAndDVD.filter";

static NSString* _tvNameKey = @"Consumption.film.tv.name";
static NSString* _tvIconKey = @"Consumption.film.tv.icon";
static NSString* _tvBackIconKey = @"Consumption.film.tv.backIcon";

//Music
static NSString* _artistIconKey = @"Consumption.music.artist.icon";
static NSString* _artistBackIconKey = @"Consumption.music.artist.back_icon";
static NSString* _artistNameKey = @"Consumption.music.artist.name";

static NSString* _albumIconKey = @"Consumption.music.album.icon";
static NSString* _albumBackIconKey = @"Consumption.music.album.back_icon";
static NSString* _albumNameKey = @"Consumption.music.album.name";

static NSString* _songIconKey = @"Consumption.music.song.icon";
static NSString* _songBackIconKey = @"Consumption.music.song.back_icon";
static NSString* _songNameKey = @"Consumption.music.song.name";

static NSString* const _subcategoryType = @"subcategory";
static NSString* const _categoryType = @"category";
static NSString* const _filterType = @"filter";

@interface STConsumptionViewController () <STScopeSliderDelegate, STConsumptionToolbarDelegate>

- (STConsumptionToolbarItem*)setupToolbarItems;

@property (nonatomic, readonly, retain) STConsumptionLazyList* lazyList;
@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString* subcategory;
@property (nonatomic, readwrite, copy) NSString* filter;
@property (nonatomic, readonly, retain) STConsumptionToolbar* consumptionToolbar;
@property (nonatomic, readonly, retain) STGenericTableDelegate* tableDelegate;

@end

@implementation STConsumptionViewController

@synthesize tableDelegate = tableDelegate_;
@synthesize lazyList = lazyList_;
@synthesize category = category_;
@synthesize scope = scope_;
@synthesize subcategory = subcategory_;
@synthesize filter = filter_;
@synthesize consumptionToolbar = consumptionToolbar_;

- (void)update {
  STConsumptionSlice* slice = [[[STConsumptionSlice alloc] init] autorelease];
  slice.category = self.category;
  if (self.subcategory) {
    slice.subcategory = self.subcategory;
  }
  slice.scope = [[STStampedAPI sharedInstance] stringForScope:self.scope];
  [lazyList_ shrinkToCount:0];
  lazyList_.genericSlice = slice;
  [tableDelegate_ reloadStampedData];
}

- (STConsumptionToolbarItem*)setupToolbarItems {
  NSMutableArray* array = [NSMutableArray array];
  if ([self.category isEqualToString:@"film"]) {
    STConsumptionToolbarItem* movie = [[[STConsumptionToolbarItem alloc] init] autorelease];
    movie.name = [STConfiguration value:_movieNameKey];
    movie.icon = [STConfiguration value:_movieIconKey];
    movie.backIcon = [STConfiguration value:_movieBackIconKey];
    movie.value = @"movie";
    movie.type = _subcategoryType;
    [array addObject:movie];
    STConsumptionToolbarItem* movieInTheaters = [[[STConsumptionToolbarItem alloc] init] autorelease];
    movieInTheaters.name = [STConfiguration value:_inTheatersNameKey];
    movieInTheaters.value = [STConfiguration value:_inTheatersFilterKey];
    movieInTheaters.icon = [STConfiguration value:_inTheatersIconKey];
    movieInTheaters.backIcon = [STConfiguration value:_inTheatersBackIconKey];
    movieInTheaters.type = _filterType;
    STConsumptionToolbarItem* movieOnlineAndDVD = [[[STConsumptionToolbarItem alloc] init] autorelease];
    movieOnlineAndDVD.name = [STConfiguration value:_onlineAndDVDNameKey];
    movieOnlineAndDVD.value = [STConfiguration value:_onlineAndDVDFilterKey];
    movieOnlineAndDVD.icon = [STConfiguration value:_onlineAndDVDIconKey];
    movieOnlineAndDVD.backIcon = [STConfiguration value:_onlineAndDVDBackIconKey];
    movieOnlineAndDVD.type = _filterType;
    movie.children = [NSArray arrayWithObjects:movieInTheaters, movieOnlineAndDVD, nil];
    
    STConsumptionToolbarItem* tv = [[[STConsumptionToolbarItem alloc] init] autorelease];
    tv.name = [STConfiguration value:_tvNameKey];
    tv.icon = [STConfiguration value:_tvIconKey];
    tv.backIcon = [STConfiguration value:_tvBackIconKey];
    tv.value = @"tv";
    tv.value = _subcategoryType;
    [array addObject:tv];
  }
  else if ([self.category isEqualToString:@"book"]) {
    //None
  }
  else if ([self.category isEqualToString:@"music"]) {
    STConsumptionToolbarItem* artist = [[[STConsumptionToolbarItem alloc] init] autorelease];
    artist.value = @"artist";
    artist.name = [STConfiguration value:_artistNameKey];
    artist.icon = [STConfiguration value:_artistIconKey];
    artist.backIcon = [STConfiguration value:_artistBackIconKey];
    artist.type = _subcategoryType;
    [array addObject:artist];
    
    STConsumptionToolbarItem* albums = [[[STConsumptionToolbarItem alloc] init] autorelease];
    albums.value = @"album";
    albums.name = [STConfiguration value:_albumNameKey];
    albums.icon = [STConfiguration value:_albumIconKey];
    albums.backIcon = [STConfiguration value:_albumBackIconKey];
    albums.type = _subcategoryType;
    [array addObject:albums];
    
    STConsumptionToolbarItem* songs = [[[STConsumptionToolbarItem alloc] init] autorelease];
    songs.value = @"song";
    songs.name = [STConfiguration value:_songNameKey];
    songs.icon = [STConfiguration value:_songIconKey];
    songs.backIcon = [STConfiguration value:_songBackIconKey];
    songs.type = _subcategoryType;
    [array addObject:songs];
  }
  else if ([self.category isEqualToString:@"other"]) {
    
  }
  STConsumptionToolbarItem* rootItem = [[[STConsumptionToolbarItem alloc] init] autorelease];
  rootItem.type = _categoryType;
  rootItem.children = [array retain];
  return rootItem;
}

- (id)initWithCategory:(NSString*)category
{
  self = [super initWithHeaderHeight:0];
  if (self) {
    category_ = [category retain];
    // Custom initialization
    scope_ = STStampedAPIScopeFriends;
    tableDelegate_ = [[STGenericTableDelegate alloc] init];
    lazyList_ = [[STConsumptionLazyList alloc] init];
    tableDelegate_.style = STCellStyleConsumption;
    tableDelegate_.lazyList = lazyList_;
    tableDelegate_.tableViewCellFactory = [STStampCellFactory sharedInstance];
    __block STConsumptionViewController* weak = self;
    tableDelegate_.tableShouldReloadCallback = ^(id<STTableDelegate> tableDelegate) {
      [weak.tableView reloadData];
    };
    STConsumptionToolbarItem* rootItem = [self setupToolbarItems];
    consumptionToolbar_ = [[STConsumptionToolbar alloc] initWithRootItem:rootItem andScope:STStampedAPIScopeFriends];
    consumptionToolbar_.slider.delegate = self;
    consumptionToolbar_.delegate = self;
    [self update];
  }
  return self;
}

- (void)dealloc
{
  [tableDelegate_ release];
  [lazyList_ release];
  [category_ release];
  [subcategory_ release];
  [filter_ release];
  [super dealloc];
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  self.tableView.delegate = self.tableDelegate;
  self.tableView.dataSource = self.tableDelegate;
	// Do any additional setup after loading the view.
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  // Release any retained subviews of the main view.
}

- (UIView *)loadToolbar {
  return self.consumptionToolbar;
}

- (void)scopeSlider:(STScopeSlider *)slider didChangeGranularity:(STStampedAPIScope)granularity {
  self.scope = granularity;
}

- (void)setScope:(STStampedAPIScope)scope {
  scope_ = scope;
  [self update];
}

- (void)toolbar:(STConsumptionToolbar*)toolbar 
  didMoveToItem:(STConsumptionToolbarItem*)item 
           from:(STConsumptionToolbarItem*)previous {
  if ([item.type isEqualToString:_categoryType]) {
    self.subcategory = nil;
    self.filter = nil;
  }
  else if ([item.type isEqualToString:_subcategoryType]) {
    self.filter = nil;
    self.subcategory = item.value;
  }
  else if ([item.type isEqualToString:_filterType]) {
    self.filter = item.value;
    self.subcategory = item.parent.value;
  }
  [self update];
}

- (void)cancelPendingRequests {
  [self.tableDelegate cancelPendingRequests];
}

- (void)reloadStampedData {
  [super reloadStampedData];
  [self.tableDelegate reloadStampedData];
}

+ (void)setupConfigurations {    
  //Film
  //Movie
  [STConfiguration addString:@"Movies" forKey:_movieNameKey];
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_movieIconKey];
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_movieBackIconKey];
  
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_inTheatersIconKey];
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_inTheatersBackIconKey];
  [STConfiguration addString:@"In Theaters" forKey:_inTheatersNameKey];
  [STConfiguration addString:@"in_theaters" forKey:_inTheatersFilterKey];
  
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_onlineAndDVDIconKey];
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_onlineAndDVDBackIconKey];
  [STConfiguration addString:@"Online/DVD" forKey:_onlineAndDVDNameKey];
  [STConfiguration addString:@"online_and_dvd" forKey:_onlineAndDVDFilterKey];
  
  //TV
  [STConfiguration addString:@"TV" forKey:_tvNameKey];
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_tvIconKey];
  [STConfiguration addString:@"cat_icon_eDetail_film" forKey:_tvBackIconKey];
  
  //Music
  //Artist
  [STConfiguration addString:@"Artists" forKey:_artistNameKey];
  [STConfiguration addString:@"cat_icon_eDetail_music" forKey:_artistIconKey];
  [STConfiguration addString:@"cat_icon_eDetail_music" forKey:_artistBackIconKey];
  
  //Album
  [STConfiguration addString:@"Albums" forKey:_albumNameKey];
  [STConfiguration addString:@"cat_icon_eDetail_music" forKey:_albumIconKey];
  [STConfiguration addString:@"cat_icon_eDetail_music" forKey:_albumBackIconKey];
  
  //Song
  [STConfiguration addString:@"Songs" forKey:_songNameKey];
  [STConfiguration addString:@"cat_icon_eDetail_music" forKey:_songIconKey];
  [STConfiguration addString:@"cat_icon_eDetail_music" forKey:_songBackIconKey];
  
  [STConsumptionToolbar setupConfigurations];
}

@end
