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
#import "STStampedAPI.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STConfiguration.h"
#import "STConsumptionToolbarItem.h"
#import "STConsumptionToolbar.h"
#import "STGenericCellFactory.h"

//Film
static NSString* _movieNameKey = @"Consumption.film.movie.name";

static NSString* _inTheatersNameKey = @"Consumption.film.movie.inTheaters.name";
static NSString* _inTheatersFilterKey = @"Consumption.film.movie.inTheaters.filter";

static NSString* _onlineAndDVDNameKey = @"Consumption.film.movie.onlineAndDVD.name";
static NSString* _onlineAndDVDFilterKey = @"Consumption.film.movie.onlineAndDVD.filter";

static NSString* _tvNameKey = @"Consumption.film.tv.name";
//Music
static NSString* _artistNameKey = @"Consumption.music.artist.name";

static NSString* _albumNameKey = @"Consumption.music.album.name";

static NSString* _songNameKey = @"Consumption.music.song.name";

@interface STConsumptionViewController () <STConsumptionToolbarDelegate>

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
    self.tableDelegate.lazyList = [[[STConsumptionLazyList alloc] initWithScope:self.scope
                                                                        section:self.category
                                                                     subsection:self.subcategory] autorelease];
    [tableDelegate_ reloadStampedData];
}

- (STConsumptionToolbarItem*)setupToolbarItems {
    NSMutableArray* array = [NSMutableArray array];
    if ([self.category isEqualToString:@"film"]) {
        STConsumptionToolbarItem* movie = [[[STConsumptionToolbarItem alloc] init] autorelease];
        movie.name = [STConfiguration value:_movieNameKey];
        movie.value = @"movie";
        movie.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:movie];
        
        /*
         STConsumptionToolbarItem* movieInTheaters = [[[STConsumptionToolbarItem alloc] init] autorelease];
         movieInTheaters.name = [STConfiguration value:_inTheatersNameKey];
         movieInTheaters.value = [STConfiguration value:_inTheatersFilterKey];
         movieInTheaters.iconValue = @"in_theaters";
         
         movieInTheaters.type = STConsumptionToolbarItemTypeFilter;
         STConsumptionToolbarItem* movieOnlineAndDVD = [[[STConsumptionToolbarItem alloc] init] autorelease];
         movieOnlineAndDVD.name = [STConfiguration value:_onlineAndDVDNameKey];
         movieOnlineAndDVD.value = [STConfiguration value:_onlineAndDVDFilterKey];
         movieOnlineAndDVD.type = STConsumptionToolbarItemTypeFilter;
         movieOnlineAndDVD.iconValue = @"online_dvd";
         movie.children = [NSArray arrayWithObjects:movieInTheaters, movieOnlineAndDVD, nil];
         */
        
        STConsumptionToolbarItem* tv = [[[STConsumptionToolbarItem alloc] init] autorelease];
        tv.name = [STConfiguration value:_tvNameKey];
        tv.value = @"tv";
        tv.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:tv];
    }
    else if ([self.category isEqualToString:@"book"]) {
        //None
    }
    else if ([self.category isEqualToString:@"music"]) {
        STConsumptionToolbarItem* artist = [[[STConsumptionToolbarItem alloc] init] autorelease];
        artist.value = @"artist";
        artist.name = [STConfiguration value:_artistNameKey];
        artist.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:artist];
        
        STConsumptionToolbarItem* albums = [[[STConsumptionToolbarItem alloc] init] autorelease];
        albums.value = @"album";
        albums.name = [STConfiguration value:_albumNameKey];
        albums.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:albums];
        
        STConsumptionToolbarItem* songs = [[[STConsumptionToolbarItem alloc] init] autorelease];
        songs.value = @"track";
        songs.iconValue = @"song";
        songs.name = [STConfiguration value:_songNameKey];
        songs.type = STConsumptionToolbarItemTypeSubsection;
        [array addObject:songs];
    }
    else if ([self.category isEqualToString:@"other"]) {
        
    }
    STConsumptionToolbarItem* rootItem = [[[STConsumptionToolbarItem alloc] init] autorelease];
    rootItem.type = STConsumptionToolbarItemTypeSection;
    rootItem.value = category_;
    rootItem.children = [array retain];
    return rootItem;
}

- (id)initWithCategory:(NSString*)category
{
    self = [super initWithHeaderHeight:0];
    if (self) {
        category_ = [category retain];
        // Custom initialization
        if (LOGGED_IN) {
            scope_ = STStampedAPIScopeFriends;
        }
        else {
            scope_ = STStampedAPIScopeEveryone;
        }
        tableDelegate_ = [[STGenericTableDelegate alloc] init];
        tableDelegate_.style = STCellStyleConsumption;
        tableDelegate_.lazyList = lazyList_;
        tableDelegate_.tableViewCellFactory = [STGenericCellFactory sharedInstance];
        __block STConsumptionViewController* weak = self;
        tableDelegate_.tableShouldReloadCallback = ^(id<STTableDelegate> tableDelegate) {
            [weak.tableView reloadData];
        };
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
}

- (UIView *)loadToolbar {
    if (LOGGED_IN) {
        STConsumptionToolbarItem* rootItem = [self setupToolbarItems];
        consumptionToolbar_ = [[STConsumptionToolbar alloc] initWithRootItem:rootItem andScope:STStampedAPIScopeFriends];
        consumptionToolbar_.slider.delegate = (id<STSliderScopeViewDelegate>)self;
        consumptionToolbar_.delegate = self;
        return consumptionToolbar_;
    }
    else {
        return nil;
    }
}

- (void)unloadToolbar {
    [consumptionToolbar_ release];
    consumptionToolbar_ = nil;
}

- (void)setScope:(STStampedAPIScope)scope {
    scope_ = scope;
    [self update];
}

- (void)toolbar:(STConsumptionToolbar*)toolbar 
  didMoveToItem:(STConsumptionToolbarItem*)item 
           from:(STConsumptionToolbarItem*)previous {
    if (item.type == STConsumptionToolbarItemTypeSection) {
        self.subcategory = nil;
        self.filter = nil;
    }
    else if (item.type == STConsumptionToolbarItemTypeSubsection) {
        self.filter = nil;
        self.subcategory = item.value;
    }
    else if (item.type == STConsumptionToolbarItemTypeFilter) {
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
    
    [STConfiguration addString:@"In Theaters" forKey:_inTheatersNameKey];
    [STConfiguration addString:@"in_theaters" forKey:_inTheatersFilterKey];
    
    [STConfiguration addString:@"Online/DVD" forKey:_onlineAndDVDNameKey];
    [STConfiguration addString:@"online_and_dvd" forKey:_onlineAndDVDFilterKey];
    
    //TV
    [STConfiguration addString:@"TV" forKey:_tvNameKey];
    
    //Music
    //Artist
    [STConfiguration addString:@"Artists" forKey:_artistNameKey];
    
    //Album
    [STConfiguration addString:@"Albums" forKey:_albumNameKey];
    
    //Song
    [STConfiguration addString:@"Songs" forKey:_songNameKey];
    
    [STConsumptionToolbar setupConfigurations];
}

#pragma mark - STSliderScopeViewDelegate

- (void)sliderScopeView:(STSliderScopeView*)slider didChangeScope:(STStampedAPIScope)scope {
    
    self.scope = scope;
    
}

@end
