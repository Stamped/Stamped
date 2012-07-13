//
//  CreateEntityViewController.m
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

#import "CreateEntityViewController.h"
#import "CountriesViewController.h"
#import "STMusicPickerViewController.h"
#import "STSegmentedControl.h"
#import "STTextFieldTableCell.h"
#import "STTextViewTableCell.h"
#import "STButtonTableCell.h"
#import "STCompressedTableCell.h"
#import "CreateStampViewController.h"
#import "STCancellation.h"
#import "Util.h"
#import "STNavigationItem.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"
#import "STAccountParameters.h"

typedef enum {
    EntityCreateTypeLocation = 0,
    EntityCreateTypeBook,
    EntityCreateTypeMusic,
    EntityCreateTypeFilm,
    EntityCreateTypeTV,
    EntityCreateTypeApp,
    EntityCreateTypeOther,
} EntityCreateType;

typedef enum {
    STTableViewPanDirectionUp = 0,
    STTableViewPanDirectionDown,
} STTableViewPanDirection;

@interface CreateEntityViewController () <UITextFieldDelegate, STTextViewTableCellDelegate>
@property(nonatomic,retain) NSArray *dataSource;
@property(nonatomic,retain) NSArray *segmentDataSource;
@property(nonatomic,retain) NSMutableArray *values;
@property(nonatomic,retain) NSMutableArray *compressedSections;
@property(nonatomic,readonly) EntityCreateType createType;
@property(nonatomic,retain) NSIndexPath *selectedIndexPath;
@property (nonatomic, readwrite, retain) UIResponder* firstResponder;
@property (nonatomic, readonly, retain) NSString* category;
@property (nonatomic, readwrite, retain) STCancellation* addCancellation;
@property (nonatomic, readwrite, retain) NSString* subcategory;

@property (nonatomic, readonly, retain) UIPanGestureRecognizer *panGesture;
@property (nonatomic, assign) STTableViewPanDirection direction;
@property (nonatomic, assign) CGRect beginFrame;

- (void)updateValue:(NSString*)value atIndexPath:(NSIndexPath*)indexPath;
- (BOOL)compressed:(NSInteger)section;

@end

@implementation CreateEntityViewController
@synthesize dataSource=_dataSource;
@synthesize segmentDataSource=_segmentDataSource;
@synthesize values=_values;
@synthesize createType=_createType;
@synthesize delegate;
@synthesize selectedIndexPath=_selectedIndexPath;
@synthesize compressedSections;
@synthesize firstResponder = _firstResponder;
@synthesize category = _category;
@synthesize subcategory = _subcategory;
@synthesize addCancellation = _addCancellation;

@synthesize panGesture=_panGesture;
@synthesize direction;
@synthesize beginFrame;

- (NSArray*)addressDataSource {
    
    return [NSArray arrayWithObjects:
            [NSDictionary dictionaryWithObjectsAndKeys:@"address line 1", @"title", nil],
            [NSDictionary dictionaryWithObjectsAndKeys:@"address line 2", @"title", nil],
            [NSDictionary dictionaryWithObjectsAndKeys:@"city", @"title", nil],
            [NSDictionary dictionaryWithObjectsAndKeys:@"state", @"title", nil],
            [NSDictionary dictionaryWithObjectsAndKeys:@"postal code", @"title", nil],
            [NSDictionary dictionaryWithObjectsAndKeys:@"country", @"title", @"STButtonTableCell", @"class", nil], nil];
    
}

- (NSDictionary*)paramsForItems:(NSDictionary*)items {
    NSMutableDictionary* result = [NSMutableDictionary dictionaryWithObject:self.category forKey:@"category"];
    NSDictionary* simpleMappings = [NSDictionary dictionaryWithObjectsAndKeys:
                                    //Common
                                    @"desc", @"description",
                                    //Other
                                    @"title", @"name",
                                    @"subtitle", @"what is it",
                                    //App
                                    @"title", @"app_name",
                                    @"author", @"creator",
                                    //Movie
                                    @"director", @"director",
                                    @"title", @"film_title",
                                    @"year", @"year",
                                    //TV
                                    @"network", @"channel",
                                    @"title", @"series_title",
                                    //Song
                                    @"artist", @"artist_name",
                                    @"title", @"song_title",
                                    //Album
                                    @"title", @"album_title",
                                    //Artist
                                    @"title", @"artist_title",
                                    //@"genre", @"genre",
                                    //Book
                                    @"title", @"book_title",
                                    @"author", @"author",
                                    //Place
                                    @"subtitle",            @"type of place",
                                    @"address_street",      @"address_line_1",
                                    @"address_street_ext",  @"address_line_2",
                                    @"address_locality",    @"city",
                                    @"address_region",      @"state",
                                    @"address_postcode",    @"postal code",
                                    @"address_country",     @"country",

                                    nil];
    for (NSString* key in simpleMappings.allKeys) {
        NSString* value = [items objectForKey:key];
        if (value) {
            [result setObject:value forKey:[simpleMappings objectForKey:key]];
        }
    }
    
    NSString* subcategory = [result objectForKey:@"subcategory"];
    if (!subcategory) {
        subcategory = self.subcategory;
        if (!subcategory) {
            if ([items objectForKey:@"song_title"]) {
                subcategory = @"song";
            }
            else if ([items objectForKey:@"album_title"]) {
                subcategory = @"album";
            }
            else if ([items objectForKey:@"app_name"]) {
                subcategory = @"app";
            }
            else if ([items objectForKey:@"film_title"]) {
                subcategory = @"movie";
            }
            else if ([items objectForKey:@"series_title"]) {
                subcategory = @"tv";
            }
            else {
                subcategory = @"other";
            }
        }
    }
    [result setObject:subcategory forKey:@"subcategory"];
    NSString* subtitle = [result objectForKey:@"subtitle"];
    if (!subtitle) {
        if ([items objectForKey:@"what is it"]) {
            subtitle = [items objectForKey:@"what is it"];
        }
        else if ([result objectForKey:@"address"]) {
            subtitle = [result objectForKey:@"address"];
        }
        else if ([result objectForKey:@"author"]) {
            subtitle = [NSString stringWithFormat:@"By %@", [result objectForKey:@"author"]];
        }
        else {
            subtitle = @"";
        }
    }
    [result setObject:subtitle forKey:@"subtitle"];
    
    if (![[result objectForKey:@"title"] length]) {
        return nil;
    }
    return result;
}

//cls.addProperty('title',                            basestring, required=True)
//cls.addProperty('subtitle',                         basestring, required=True)
//cls.addProperty('category',                         basestring, required=True)
//cls.addProperty('subcategory',                      basestring, required=True)
- (NSArray*)descriptionDataSource {
    
    return [NSArray arrayWithObject:[NSDictionary dictionaryWithObjectsAndKeys:@"decription", @"title", @"STTextViewTableCell", @"class", nil]];
    
}

- (id)initWithEntityCategory:(NSString*)category entityTitle:(NSString *)title {
    
    EntityCreateType type = [CreateEntityViewController entityCreateTypeForCategory:category];
    // style is UITableViewStyleGrouped so section headers don't stick
    if ((self = [super initWithStyle:UITableViewStyleGrouped])) {
        _category = [category retain];
        _createType = type;
        
        NSMutableArray *dataSource = [[NSMutableArray alloc] init];
        
        /* data source key value store options */
        
        /*
         * title -> title - string
         * detailTitleLabel -> detail title - string
         * placeholder -> text field place holder - string
         * class -> table view cell class name - string
         */
        
        switch (type) {
            case EntityCreateTypeLocation: {
                self.subcategory = @"restaurant";
                [dataSource addObject:[NSArray arrayWithObject:[NSDictionary dictionaryWithObjectsAndKeys:@"name", @"title", nil]]];
                [dataSource addObject:[self addressDataSource]];
                [dataSource addObject:[self descriptionDataSource]];
                
                self.segmentDataSource = [NSArray arrayWithObjects:@"Restaurant", @"Bar", @"Café", @"Other", nil];
                self.compressedSections = [NSMutableArray arrayWithObjects:[NSNull null], @"Add location", @"Add decription", nil];
                
            }
                break;
            case EntityCreateTypeMusic: {
                
                [dataSource addObject:[NSArray arrayWithObjects:
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"song title", @"title", nil],
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"artist name", @"title", nil], nil]];
                
                [dataSource addObject:[NSArray arrayWithObject:
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"Choose artist from Music Library", @"title", @"STButtonTableCell", @"class", nil]]];
                
                self.segmentDataSource = [NSArray arrayWithObjects:@"Song", @"Album", @"Artist", nil];
                self.compressedSections = [NSMutableArray arrayWithObjects:[NSNull null], [NSNull null], nil];
                
            }
                break;
            case EntityCreateTypeBook: {
                
                [dataSource addObject:[NSArray arrayWithObjects:
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"book title", @"title", nil],
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"author", @"title", nil], nil]];
                [dataSource addObject:[self descriptionDataSource]];
                
                self.compressedSections = [NSMutableArray arrayWithObjects:[NSNull null], @"Add decription", nil];
                
            }
                break;
            case EntityCreateTypeFilm: {
                
                [dataSource addObject:[NSArray arrayWithObjects:
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"film title", @"title", nil],
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"director", @"title", nil],
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"year", @"title", nil], nil]];
                [dataSource addObject:[self descriptionDataSource]];
                
                self.segmentDataSource = [NSArray arrayWithObjects:@"Film", @"TV Series", nil];
                self.compressedSections = [NSMutableArray arrayWithObjects:[NSNull null],  @"Add decription", nil];
                
            }
                break;
            case EntityCreateTypeApp: {
                
                [dataSource addObject:[NSArray arrayWithObjects:
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"app name", @"title", nil],
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"creator", @"title", nil], nil]];
                [dataSource addObject:[self descriptionDataSource]];
                
                self.compressedSections = [NSMutableArray arrayWithObjects:[NSNull null],  @"Add decription", nil];
                
            }
                break;
            case EntityCreateTypeOther: {
                
                [dataSource addObject:[NSArray arrayWithObjects:
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"name", @"title", nil],
                                       [NSDictionary dictionaryWithObjectsAndKeys:@"what is it?", @"title", @"e.g. wine, electronics", @"placeholder", nil], nil]];
                [dataSource addObject:[self descriptionDataSource]];
                
                self.compressedSections = [NSMutableArray arrayWithObjects:[NSNull null],  @"Add decription", nil];
                
            }
                break;
            default:
                break;
        }
        
        self.dataSource = dataSource;
        [dataSource release];
        
        
        self.values = [NSMutableArray arrayWithCapacity:[self.dataSource count]];
        
        for (NSArray *array in self.dataSource) {
            NSMutableArray *sectionValues = [[NSMutableArray alloc] initWithCapacity:[array count]];
            for (NSInteger i = 0; i < [array count]; i++) {
                [sectionValues addObject:[NSNull null]];
            }
            [self.values addObject:sectionValues];
            [sectionValues release];
        }
        
        
        
        if (type == EntityCreateTypeLocation) {
            
            // fill in the country value
            NSIndexPath *indexPath = [NSIndexPath indexPathForRow:5 inSection:1];
            NSString *currentCountry = [[NSLocale currentLocale] objectForKey:NSLocaleCountryCode];
            currentCountry = [[NSLocale currentLocale] displayNameForKey:NSLocaleCountryCode value:currentCountry];
            [self updateValue:currentCountry atIndexPath:indexPath];
            
        }
        
        if (title) {
            self.title = [Util truncateTitleForBackButton:title];
            [self updateValue:title atIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
        }
        
    }
    return self;
    
}


- (void)dealloc {
    
    self.compressedSections = nil;
    self.segmentDataSource = nil;
    self.values = nil;
    self.dataSource = nil;
    self.selectedIndexPath = nil;
    self.firstResponder = nil;
    [_addCancellation cancel];
    [_addCancellation release];
    [_category release];
    [_subcategory release];
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}

- (void)useAddButton {
    STNavigationItem* button = [[[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Add", @"Add") style:UIBarButtonItemStyleDone target:self action:@selector(add:)] autorelease];
    self.navigationItem.rightBarButtonItem = button;
}

- (void)done:(id)notImportant {
    [self useAddButton];
    UIResponder* responder = self.firstResponder;
    self.firstResponder = nil;
    [responder resignFirstResponder];
}

- (void)useDoneButtonWithFirstResponder:(UIResponder*)firstResponder {
    self.firstResponder = firstResponder;
    STNavigationItem* button = [[[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Done", @"Done") style:UIBarButtonItemStyleDone target:self action:@selector(done:)] autorelease];
    self.navigationItem.rightBarButtonItem = button;
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.contentInset = UIEdgeInsetsMake(0.0f, 0.0f, -200.0f, 0.0f);
    self.tableView.backgroundColor = [UIColor colorWithWhite:0.901f alpha:1.0f];
    
    if (!self.navigationItem.leftBarButtonItem) {
        STNavigationItem *cancelButton = [[[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") 
                                                                            style:UIBarButtonItemStyleBordered
                                                                           target:self 
                                                                           action:@selector(cancel:)] autorelease];
        self.navigationItem.leftBarButtonItem = cancelButton;
    }
    [self useAddButton];
    
    if (self.segmentDataSource && [self.segmentDataSource count] > 0) {
        STSegmentedControl *segment = [[STSegmentedControl alloc] initWithItems:self.segmentDataSource];
        [segment addTarget:self action:@selector(segmentChanged:) forControlEvents:UIControlEventValueChanged];
        self.tableView.tableHeaderView = segment;
        [segment release];
    }
    
    STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
    background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
        drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
    }];
    self.tableView.backgroundView = background;
    [background release];
    
    UIImage *image = [UIImage imageNamed:@"entity_create_footer_shadow.png"];
    UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
    imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    imageView.frame = CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, image.size.height);
    self.tableView.tableFooterView = imageView;
    [imageView release];
    /*
     if (!_panGesture) {
     UIPanGestureRecognizer *pan = [[UIPanGestureRecognizer alloc] initWithTarget:self action:@selector(pan:)];
     pan.delegate = (id<UIGestureRecognizerDelegate>)self;
     [self.tableView addGestureRecognizer:pan];
     _panGesture = [pan retain];
     [pan setEnabled:NO];
     [pan release];
     }
     */
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];    
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillShow:) name:UIKeyboardWillShowNotification object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(keyboardWillHide:) name:UIKeyboardWillHideNotification object:nil];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    [[NSNotificationCenter defaultCenter] removeObserver:self];
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    [Util compareAndPopController:self animated:YES];
    
}

- (void)add:(id)sender {
    if (self.addCancellation) return;
    
    NSMutableDictionary *entityDictionary = [[NSMutableDictionary alloc] init];
    
    NSInteger section = 0;
    for (NSArray *array in self.dataSource) {
        for (NSInteger i = 0; i < [array count]; i++) {
            
            id obj = [array objectAtIndex:i];
            id value = [self valueForIndexPath:[NSIndexPath indexPathForRow:i inSection:section]];
            if (value && ![value isEqual:[NSNull null]]) {
                
                NSString *key = [[[obj objectForKey:@"title"] stringByReplacingOccurrencesOfString:@" " withString:@"_"] lowercaseString];
                [entityDictionary setObject:value forKey:key];
                
            }
            
        }
        section++;
    }
    
    
    // POST new entity
    NSLog(@"entity : %@", [entityDictionary description]);
    
    NSDictionary* params = [self paramsForItems:entityDictionary];
    if (params) {
        self.addCancellation = [[STStampedAPI sharedInstance] createEntityWithParams:params
                                                                         andCallback:^(id<STEntityDetail> entityDetail, NSError *error, STCancellation *cancellation) {
                                                                             self.addCancellation = nil;
                                                                             if (entityDetail) {
                                                                                 CreateStampViewController* controller = [[[CreateStampViewController alloc] initWithEntity:entityDetail] autorelease];
                                                                                 [Util pushController:controller modal:NO animated:YES];
                                                                             }
                                                                             else {
                                                                                 [Util warnWithAPIError:error andBlock:^{
                                                                                     [Util compareAndPopController:self animated:YES];
                                                                                 }];
                                                                             }
                                                                         }];
    }
    else {
        [Util warnWithMessage:@"You must at enter a name" andBlock:nil];
    }
}

- (void)segmentChanged:(STSegmentedControl*)segmentedControl {
    
    NSMutableArray *mutableDataSource = [self.dataSource mutableCopy];
    
    if (_createType == EntityCreateTypeLocation) {
        
        switch (segmentedControl.selectedSegmentIndex) {
                
            case 3:
                self.subcategory = @"establishment";
                // other
                [mutableDataSource replaceObjectAtIndex:0 withObject:
                 [NSArray arrayWithObjects:
                  [NSDictionary dictionaryWithObjectsAndKeys:@"name", @"title", nil],
                  [NSDictionary dictionaryWithObjectsAndKeys:@"type of place", @"title", @"e.g. hotel, store, museum", @"placeholder", nil], nil]];
                
                break;
                
            case 0:
                self.subcategory =  @"restaurant";
                [mutableDataSource replaceObjectAtIndex:0 withObject:
                 [NSArray arrayWithObject:[NSDictionary dictionaryWithObjectsAndKeys:@"name", @"title", nil]]];
                break;
            case 1:
                self.subcategory = @"bar";
                [mutableDataSource replaceObjectAtIndex:0 withObject:
                 [NSArray arrayWithObject:[NSDictionary dictionaryWithObjectsAndKeys:@"name", @"title", nil]]];
                break;
            case 2:
                self.subcategory = @"cafe";
                [mutableDataSource replaceObjectAtIndex:0 withObject:
                 [NSArray arrayWithObject:[NSDictionary dictionaryWithObjectsAndKeys:@"name", @"title", nil]]];
                break;
            default:
                
                // restaurant, bar, cafe
                [mutableDataSource replaceObjectAtIndex:0 withObject:
                 [NSArray arrayWithObject:[NSDictionary dictionaryWithObjectsAndKeys:@"name", @"title", nil]]];
                break;
        }
        
        
    } else if (_createType == EntityCreateTypeMusic) {
        
        switch (segmentedControl.selectedSegmentIndex) {
                
            case 1:
                
                // album
                [mutableDataSource replaceObjectAtIndex:0 withObject:[NSArray arrayWithObjects:
                                                                      [NSDictionary dictionaryWithObjectsAndKeys:@"album title", @"title", nil],
                                                                      [NSDictionary dictionaryWithObjectsAndKeys:@"artist name", @"title", nil], nil]];
                break;
            case 2:
                
                // artist
                [mutableDataSource replaceObjectAtIndex:0 withObject:[NSArray arrayWithObjects:
                                                                      [NSDictionary dictionaryWithObjectsAndKeys:@"artist title", @"title", nil],
                                                                      [NSDictionary dictionaryWithObjectsAndKeys:@"genre", @"title", nil], nil]];
                break;
                
            case 0:
            default:
                
                // song
                [mutableDataSource replaceObjectAtIndex:0 withObject:[NSArray arrayWithObjects:
                                                                      [NSDictionary dictionaryWithObjectsAndKeys:@"song title", @"title", nil],
                                                                      [NSDictionary dictionaryWithObjectsAndKeys:@"artist name", @"title", nil], nil]];
                
                break;
        }
        
        
    } else if (_createType == EntityCreateTypeFilm) {
        
        // film, tv series
        NSInteger index = segmentedControl.selectedSegmentIndex;
        [mutableDataSource replaceObjectAtIndex:0 withObject:[NSArray arrayWithObjects:
                                                              [NSDictionary dictionaryWithObjectsAndKeys:(index==0) ? @"film title" : @"series title", @"title", nil],
                                                              [NSDictionary dictionaryWithObjectsAndKeys:(index==0) ? @"director" : @"channel", @"title", (index==0) ? @"" : @"e.g. NBC, HBO, Bravo", @"placeholder", nil],
                                                              [NSDictionary dictionaryWithObjectsAndKeys:@"year", @"title", nil], nil]];
        
        
    }
    
    
    [_dataSource release], _dataSource=nil;
    _dataSource = [mutableDataSource retain];
    [mutableDataSource release];
    
    NSInteger rows = [self.tableView numberOfRowsInSection:0];
    NSInteger newRows = [(NSArray*)[_dataSource objectAtIndex:0] count];
    
    
    // reload section 0
    if (newRows > rows) {
        
        [self.tableView beginUpdates];
        NSMutableArray *indexPaths = [[NSMutableArray alloc] initWithCapacity:newRows-rows];
        for (NSInteger i = rows; i < newRows; i++) {
            [indexPaths addObject:[NSIndexPath indexPathForRow:i inSection:0]];
            [[self.values objectAtIndex:0] insertObject:[NSNull null] atIndex:i];
        }
        [self.tableView insertRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationFade];
        [indexPaths release];
        [self.tableView endUpdates];
        
    } else if (newRows < rows) {
        
        [self.tableView beginUpdates];
        NSMutableArray *indexPaths = [[NSMutableArray alloc] initWithCapacity:rows-newRows];
        for (NSInteger i = rows; i > newRows; i--) {
            [indexPaths addObject:[NSIndexPath indexPathForRow:i-1 inSection:0]];
            [[self.values objectAtIndex:0] removeObjectAtIndex:i-1];
        }
        [self.tableView deleteRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationFade];
        [indexPaths release];
        [self.tableView endUpdates];
        
    } else {
        [self.tableView reloadData];
    }
    
    
    
}


#pragma mark - STButtonTableCellDelegate

- (void)stButtonTableCellSelected:(STButtonTableCell*)cell {
    
    self.selectedIndexPath = [self.tableView indexPathForCell:cell];
    
    if (_createType == EntityCreateTypeMusic) {
        
        STSegmentedControl *segmentControl = (STSegmentedControl*)self.tableView.tableHeaderView;
        STMusicPickerViewController *controller = [[STMusicPickerViewController alloc] initWithQueryType:segmentControl.selectedSegmentIndex];
        controller.delegate = (id<STMusicPickerViewControllerDelegate>)self;
        [self.navigationController pushViewController:controller animated:YES];
        [controller release];
        
    } 
    else {
        CountriesViewController *controller = [[CountriesViewController alloc] init];
        controller.selectedCountry = [self valueForIndexPath:[self.tableView indexPathForCell:cell]];
        controller.delegate = (id<CountriesViewControllerDelegate>)self;
        [self.navigationController pushViewController:controller animated:YES];
        [controller release];
    }
    
}


#pragma mark - STMusicPickerViewControllerDelegate

- (void)stMusicPickerController:(STMusicPickerViewController*)controller didPickMediaItem:(MPMediaItem*)item {
    
    NSString *albumKey = [MPMediaItem titlePropertyForGroupingType:MPMediaGroupingAlbum];
    NSString *songKey = [MPMediaItem titlePropertyForGroupingType:MPMediaGroupingTitle];
    NSString *artistKey = [MPMediaItem titlePropertyForGroupingType:MPMediaGroupingArtist];
    NSString *genreKey = [MPMediaItem titlePropertyForGroupingType:MPMediaGroupingGenre];
    
    STSegmentedControl *segmentControl = (STSegmentedControl*)self.tableView.tableHeaderView;
    
    switch (segmentControl.selectedSegmentIndex) {
        case 0:
            
            // song
            [self updateValue:[item valueForProperty:songKey] atIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
            [self updateValue:[item valueForProperty:artistKey] atIndexPath:[NSIndexPath indexPathForRow:1 inSection:0]];
            
            break;
            
        case 1:
            
            // album
            [self updateValue:[item valueForProperty:albumKey] atIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
            [self updateValue:[item valueForProperty:artistKey] atIndexPath:[NSIndexPath indexPathForRow:1 inSection:0]];
            
            break;
            
        case 2:
            
            // artist
            [self updateValue:[item valueForProperty:artistKey] atIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
            [self updateValue:[item valueForProperty:genreKey] atIndexPath:[NSIndexPath indexPathForRow:1 inSection:0]];
            
            break;
            
        default:
            break;
    }
    
    
    self.title = [self valueForIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];    
    [self.tableView reloadData];
    [self.navigationController popViewControllerAnimated:YES];
    
}

- (void)setTitle:(NSString *)title {
    [super setTitle:[Util truncateTitleForBackButton:title]];
}


#pragma mark - STTextViewTableCellDelegate

- (void)stTextViewTableCell:(STTextViewTableCell*)cell heightChangedFrom:(CGFloat)height to:(CGFloat)newHeight {
    //    [self.tableView reloadData];
    [self.tableView beginUpdates];
    [self.tableView endUpdates];
    
    CGFloat delta = newHeight - height;
    
    if (delta > 0) {
        CGPoint offset = self.tableView.contentOffset;
        offset.y += delta;
        [self.tableView setContentOffset:offset animated:YES];
    }
}

- (void)stTextViewTableCell:(STTextViewTableCell*)cell textChanged:(UITextView *)textView {
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    if (indexPath) {
        [self updateValue:textView.text atIndexPath:indexPath];
    }
    
}

- (void)stTextViewTableCellDidBeginEditing:(STTextViewTableCell *)cell {
    [self useDoneButtonWithFirstResponder:cell.textView];
    NSIndexPath *indexPath = [self.tableView indexPathForCell:cell];
    if (indexPath) {
        [self.tableView scrollToRowAtIndexPath:indexPath atScrollPosition:UITableViewScrollPositionTop animated:YES];
    }
}

- (void)stTextViewTableCellDidEndEditing:(STTextViewTableCell *)cell {
    [self useAddButton];
}


#pragma mark - CountriesViewController

- (void)contriesViewController:(CountriesViewController*)controller selectedCountry:(NSString*)country {
    
    if (self.selectedIndexPath) {
        [self updateValue:country atIndexPath:self.selectedIndexPath];
        self.selectedIndexPath = nil;
        [self.tableView reloadData];
    }
    
    [self.navigationController popViewControllerAnimated:YES];
    
}

- (void)contriesViewControllerCancelled:(CountriesViewController*)controller {
    [self.navigationController popViewControllerAnimated:YES];
}


#pragma mark - DataSource Helpers

- (BOOL)compressed:(NSInteger)section {
    
    id value = [self.compressedSections objectAtIndex:section];
    if ([value isEqual:[NSNull null]]) {
        return NO;
    }
    return YES;
    
}

- (id)valueForIndexPath:(NSIndexPath*)indexPath {
    
    id value = [[self.values objectAtIndex:indexPath.section] objectAtIndex:indexPath.row];
    if ([value isEqual:[NSNull null]]) {
        return nil;
    }
    
    return value;
    
}

- (void)updateValue:(NSString*)value atIndexPath:(NSIndexPath*)indexPath {
    if (!value) return; // ignore nil values
    
    NSMutableArray *array = [self.values objectAtIndex:indexPath.section];
    [array replaceObjectAtIndex:indexPath.row withObject:value];
    [self.values replaceObjectAtIndex:indexPath.section withObject:array];
    
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if ([self compressed:indexPath.section]) {
        return 40;
    }
    
    // description cell height
    NSArray *index = [self.dataSource objectAtIndex:indexPath.section];
    id obj = [index objectAtIndex:indexPath.row];
    if ([obj objectForKey:@"class"] && [[obj objectForKey:@"class"] isEqualToString:@"STTextViewTableCell"]) {
        id value = [self valueForIndexPath:indexPath];
        return [STTextViewTableCell heightForText:value];
    }
    
    return 48.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    
    if ([self compressed:section]) {
        return 1;
    }
    
    id obj = [self.dataSource objectAtIndex:section];
    
    if ([obj isKindOfClass:[NSArray class]]) {
        return [(NSArray*)obj count];
    }
    
    return 1;
    
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    
    return [self.dataSource count];
    
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if ([self compressed:indexPath.section]) {
        
        static NSString *CompressedCellIdentifier = @"CompressedCellIdentifier";
        STCompressedTableCell *cell = [tableView dequeueReusableCellWithIdentifier:CompressedCellIdentifier];
        if (cell == nil) {
            cell = [[[STCompressedTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CompressedCellIdentifier] autorelease];
        }
        
        cell.titleLabel.text = [self.compressedSections objectAtIndex:indexPath.section];
        return cell;
        
    }
    
    
    NSArray *index = [self.dataSource objectAtIndex:indexPath.section];
    id obj = [index objectAtIndex:indexPath.row];
    
    // table cell class from data source
    if ([obj objectForKey:@"class"]) {
        
        NSString *classString = [obj objectForKey:@"class"];
        Class cellClass = NSClassFromString(classString);
        
        id cell = [tableView dequeueReusableCellWithIdentifier:classString];
        if (cell == nil) {
            cell = [[[cellClass alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:classString] autorelease];
            if ([cell respondsToSelector:@selector(delegate)]) {
                [cell setDelegate:self];
            }
            
        }
        if ([obj objectForKey:@"title"] && [cell respondsToSelector:@selector(titleLabel)]) {
            [cell titleLabel].text = [obj objectForKey:@"title"];
        }
        
        
        id value = [self valueForIndexPath:indexPath];
        if (value) {
            if ([cell respondsToSelector:@selector(detailTitleLabel)]) {
                [cell detailTitleLabel].text = value;
            }
            if ([cell respondsToSelector:@selector(textView)]) {
                [cell textView].text = value;
            }
        }
        
        return cell;
        
    }
    
    
    // default STTextFieldTableCell
    static NSString *CellIdentifier = @"CellIdentifer";
    
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    
    if (cell == nil) {
        cell = [[[STTextFieldTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.titleLabel.textAlignment = UITextAlignmentRight;
        cell.titleLabel.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        cell.textField.delegate = (id<UITextFieldDelegate>)self;
        cell.textField.returnKeyType = UIReturnKeyNext;
        //cell.textField.enablesReturnKeyAutomatically = YES;
        cell.textField.delegate = self;
        [cell.textField addTarget:self action:@selector(stTextFieldTextDidChange:) forControlEvents:UIControlEventEditingChanged];
    }
    
    if ([obj objectForKey:@"title"]) {
        cell.titleLabel.text = [obj objectForKey:@"title"];
    }
    if ([obj objectForKey:@"placeholder"]) {
        cell.textField.placeholder = [obj objectForKey:@"placeholder"];
    }
    cell.textField.text = [self valueForIndexPath:indexPath];
    
    return cell;
    
}


#pragma mark - UITableViewDelegate

- (CGFloat)tableView:(UITableView *)tableView heightForHeaderInSection:(NSInteger)section {
    
    if (self.createType == EntityCreateTypeMusic && section == 1) {
        return 20.0f;
    }
    
    return 10.0f;
}

- (UIView *)tableView:(UITableView *)tableView viewForHeaderInSection:(NSInteger)section {
    
    CGFloat height = (self.createType == EntityCreateTypeMusic && section == 1) ? 20.0f : 10.0f; 
    UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, tableView.bounds.size.width, height)];
    view.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    view.backgroundColor = [UIColor clearColor];
    
    if (self.createType == EntityCreateTypeMusic && section == 1) {
        
        CAShapeLayer *layer = [CAShapeLayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.0f].CGColor;
        layer.strokeColor = [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.15f].CGColor;
        layer.lineDashPattern = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1], [NSNumber numberWithFloat:2], nil];
        layer.frame = CGRectMake(15.0f, 8.0f, 134.0f, 1.0f);
        layer.path = [UIBezierPath bezierPathWithRect:layer.bounds].CGPath;
        layer.strokeEnd = .5;
        [view.layer addSublayer:layer];
        
        layer = [CAShapeLayer layer];
        layer.contentsScale = [[UIScreen mainScreen] scale];
        layer.fillColor = [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.0f].CGColor;
        layer.strokeColor = [UIColor colorWithRed:0.0f green:0.0f blue:0.0f alpha:0.15f].CGColor;
        layer.lineDashPattern = [NSArray arrayWithObjects:[NSNumber numberWithFloat:1], [NSNumber numberWithFloat:2], nil];
        layer.frame = CGRectMake(view.bounds.size.width - (15.0f+134.0f), 8.0f, 134.0f, 1.0f);
        layer.path = [UIBezierPath bezierPathWithRect:layer.bounds].CGPath;
        layer.strokeEnd = .5;
        [view.layer addSublayer:layer];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleRightMargin;
        label.shadowColor = [UIColor whiteColor];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.font = [UIFont systemFontOfSize:10];
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.text = @"or";
        [label sizeToFit];
        [view addSubview:label];
        [label release];
        
        CGRect frame = label.frame;
        frame.origin.x = floorf((view.bounds.size.width-frame.size.width)/2);
        frame.origin.y = 0.0f;
        label.frame = frame;
        
    } else {
        
        UIView *keyline = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, view.bounds.size.width, 1.0f)];
        keyline.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        keyline.backgroundColor = [UIColor colorWithWhite:0.0f alpha:0.05f];
        [view addSubview:keyline];
        [keyline release];
        
        keyline = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 1.0f, view.bounds.size.width, 1.0f)];
        keyline.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        keyline.backgroundColor = [UIColor colorWithWhite:1.0f alpha:0.6f];
        [view addSubview:keyline];
        [keyline release];
        
    }
    
    return [view autorelease];
    
}

- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    
    if ([self compressed:indexPath.section]) {
        
        // uncompress section
        [self.compressedSections replaceObjectAtIndex:indexPath.section withObject:[NSNull null]];
        [tableView beginUpdates];
        [tableView reloadSections:[NSIndexSet indexSetWithIndex:indexPath.section] withRowAnimation:UITableViewRowAnimationFade];
        [tableView endUpdates];
        
        /* show keyboard
         id cell = [tableView cellForRowAtIndexPath:indexPath];
         if ([cell respondsToSelector:@selector(textField)]) {
         [[cell textField] becomeFirstResponder];
         } else if ([cell respondsToSelector:@selector(textView)]) {
         [[cell textView] becomeFirstResponder];
         }
         */
        
    }
    
    
}



#pragma mark - UITextFieldDelegate

- (void)textFieldDidBeginEditing:(UITextField *)textField {
    [self useDoneButtonWithFirstResponder:textField];
    NSIndexPath *indexPath = [self.tableView indexPathForCell:(UITableViewCell*)textField.superview];
    if (indexPath) {
        [Util executeOnMainThread:^{
            [self.tableView scrollToRowAtIndexPath:indexPath atScrollPosition:UITableViewScrollPositionTop animated:YES];   
        }];
    }
    
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
    [self useAddButton];
}


- (UIResponder*)firstResponderWithIndexPath:(NSIndexPath*)indexPath {
    id cell = [self.tableView cellForRowAtIndexPath:indexPath];
    if ([cell isKindOfClass:[STTextViewTableCell class]]) {
        return [cell textView];
    }
    else if ([cell isKindOfClass:[STTextFieldTableCell class]]) {
        return [cell textField];
    }
    return nil;
}

- (BOOL)hasFirstResponderWithIndexPath:(NSIndexPath*)indexPath {
    return [self firstResponderWithIndexPath:indexPath] != nil;
}

- (NSIndexPath*)nextTextCellPathForPath:(NSIndexPath*)indexPath wraps:(BOOL)wraps {
    if (!indexPath) return nil;
    NSIndexPath* next = nil;
    if (indexPath.row + 1 < [self tableView:self.tableView numberOfRowsInSection:indexPath.section]) {
        next = [NSIndexPath indexPathForRow:indexPath.row + 1 inSection:indexPath.section];
    }
    else if (indexPath.section + 1 < [self numberOfSectionsInTableView:self.tableView] && [self tableView:self.tableView numberOfRowsInSection:indexPath.section + 1] > 0) {
        next = [NSIndexPath indexPathForRow:0 inSection:indexPath.section + 1];
    }
    else if (wraps && [self numberOfSectionsInTableView:self.tableView] > 0 && [self tableView:self.tableView numberOfRowsInSection:0] > 0) {
        next = [NSIndexPath indexPathForRow:0 inSection:0];
        wraps = NO;
    }
    if (next) {
        if (![self hasFirstResponderWithIndexPath:next]) {
            next = [self nextTextCellPathForPath:next wraps:wraps];
        }
    }
    return next;
}

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    
    self.firstResponder = nil;
    NSIndexPath *indexPath = [self.tableView indexPathForCell:(UITableViewCell*)textField.superview];
    NSIndexPath *next = [self nextTextCellPathForPath:indexPath wraps:YES];
    if (next) {
        UIResponder* nextResponder = [self firstResponderWithIndexPath:next];
        [nextResponder becomeFirstResponder];
    }
    else {
        [textField resignFirstResponder];
    }
    return NO;
}

#pragma mark STTextField Actions

- (void)stTextFieldTextDidChange:(UITextField*)textField {
    
    NSIndexPath *indexPath = [self.tableView indexPathForCell:(UITableViewCell*)textField.superview];
    if (indexPath) {
        
        if (indexPath.row == 0 && indexPath.section == 0) {
            self.title = textField.text;
            [self.navigationController.navigationBar setNeedsDisplay];
        }
        [self updateValue:textField.text atIndexPath:indexPath];
        //[self.tableView scrollToRowAtIndexPath:indexPath atScrollPosition:UITableViewScrollPositionTop animated:YES];
    }
    
}

#pragma mark STTextView actions

#pragma mark - Gestures

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldRecognizeSimultaneouslyWithGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer {
    return YES;
}

- (void)pan:(UIPanGestureRecognizer*)gesture {
    
    __block CGPoint translation = [gesture translationInView:self.tableView];
    
    __block UIWindow *window = nil;
    for (UIWindow *aWindow in [[UIApplication sharedApplication] windows]) {
        if ([aWindow isKindOfClass:NSClassFromString(@"UITextEffectsWindow")]) {
            window = aWindow;
            break;
        }
    }
    if (window==nil) {
        return;
    }
    
    if (gesture.state == UIGestureRecognizerStateBegan) {
        beginFrame = window.frame;
        direction = STTableViewPanDirectionUp;
    } 
    
    if (gesture.state == UIGestureRecognizerStateChanged || gesture.state == UIGestureRecognizerStateBegan) {
        
        CGFloat maxOffsetY = floorf(self.view.superview.bounds.size.height - (window.frame.origin.y-20.0f));
        
        CGFloat prevY = window.frame.origin.y;
        CGRect frame = window.frame;
        CGFloat offsetY = MAX(beginFrame.origin.y, beginFrame.origin.y + translation.y);
        offsetY = MIN(offsetY, floorf(beginFrame.origin.y+maxOffsetY));
        frame.origin.y = offsetY;
        window.frame = frame;
        
        if (frame.origin.y != prevY) {
            direction = (frame.origin.y >= prevY) ? STTableViewPanDirectionDown : STTableViewPanDirectionUp;
        } 
        
        
    } else if (gesture.state == UIGestureRecognizerStateEnded || gesture.state == UIGestureRecognizerStateCancelled) {
        
        // max this animation would move in pts
        CGFloat maxOffsetY = ((self.view.superview.bounds.size.height) - window.frame.origin.y);
        
        if (direction==STTableViewPanDirectionUp) {
            
            // calulate animation duration
            CGFloat diff = (window.frame.origin.y - beginFrame.origin.y);
            float duration = (.3/maxOffsetY)*diff;
            
            [UIView animateWithDuration:duration animations:^{
                window.frame = beginFrame;
            }];
            
        } else {
            
            CGFloat diff = ((self.view.superview.bounds.size.height) - window.frame.origin.y);
            float duration = (.3/maxOffsetY)*diff;
            
            [UIView animateWithDuration:duration animations:^{
                
                CGRect frame = window.frame;
                frame.origin.y += diff;
                window.frame = frame;
                
                //self.tableView.contentInset = UIEdgeInsetsZero;
                
                
            } completion:^(BOOL finished) {
                
                window.frame = beginFrame;
                BOOL _enabled = [UIView areAnimationsEnabled];
                [UIView setAnimationsEnabled:NO];
                [self.tableView endEditing:YES];
                [UIView setAnimationsEnabled:_enabled];
                
            }];
            
        }
        
    }
    
}


#pragma mark - UIKeyboard Notfications

- (void)keyboardWillShow:(NSNotification*)notification {    
    
    //[self.panGesture setEnabled:YES];
    
}

- (void)keyboardWillHide:(NSNotification*)notification {
    
    //[self.panGesture setEnabled:NO];
    
}

+ (EntityCreateType)entityCreateTypeForCategory:(NSString*)category {
    if (!category) {
        return EntityCreateTypeOther;
    }
    else if ([category isEqualToString:@"place"]) {
        return EntityCreateTypeLocation;
    }
    else if ([category isEqualToString:@"book"]) {
        return EntityCreateTypeBook;
    }
    else if ([category isEqualToString:@"music"]) {
        return EntityCreateTypeMusic;
    }
    else if ([category isEqualToString:@"film"]) {
        return EntityCreateTypeFilm;
    }
    else if ([category isEqualToString:@"app"]) {
        return EntityCreateTypeApp;
    }
    return EntityCreateTypeOther;
}

@end
