//
//  STPlayerPopUp.m
//  Stamped
//
//  Created by Landon Judkins on 6/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STPlayerPopUp.h"
#import "STPlayer.h"
#import <QuartzCore/QuartzCore.h>
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "Util.h"
#import "STImageCache.h"
#import "STRippleBar.h"

@interface STPlayerPopUpCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier;
- (void)setupWithPlaylistItem:(id<STPlaylistItem>)item;

@end

@interface STPlayerPopUp () <UITableViewDataSource, UITableViewDelegate>

@property (nonatomic, readonly, retain) UITableView* tableView;
@property (nonatomic, readonly, retain) STPlayer* player;
@property (nonatomic, readonly, retain) UIButton* editButton;
@property (nonatomic, readonly, retain) UIView* headerView;
@property (nonatomic, readonly, retain) UILabel* titleView;
@property (nonatomic, readonly, retain) UILabel* subtitleView;
@property (nonatomic, readonly, retain) UIImageView* imageView;
@property (nonatomic, readonly, retain) UIView* footerView;
@property (nonatomic, readwrite, assign) BOOL selectMask;
@property (nonatomic, readonly, retain) UIButton* pauseButton;
@property (nonatomic, readonly, assign) BOOL fullFooter;

@end

@implementation STPlayerPopUp

@synthesize tableView = _tableView;
@synthesize player = _player;
@synthesize editButton = _editButton;
@synthesize headerView = _headerView;
@synthesize footerView = _footerView;
@synthesize selectMask = _selectMask;
@synthesize titleView = _titleView;
@synthesize imageView = _imageView;
@synthesize subtitleView = _subtitleView;
@synthesize pauseButton = _pauseButton;
@synthesize fullFooter = _fullFooter;

- (id)init
{
    self = [super initWithFrame:CGRectMake(15, 35, 290, 360)];
    if (self) {
        self.backgroundColor = [UIColor whiteColor];
        
        
        _fullFooter = NO;
        
        CGFloat headerHeight = 66;
        CGFloat footerHeight;
        if (_fullFooter) {
            footerHeight = 50;
        }
        else {
            footerHeight = 10;
        }
        CGFloat xOffset = 65;
        
        _player = [[STPlayer sharedInstance] retain];
        _headerView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, self.frame.size.width, headerHeight)];
        _headerView.backgroundColor = [UIColor whiteColor];
        //_headerView.clipsToBounds = YES;
        _headerView.layer.shadowOffset = CGSizeMake(0, 2);
        _headerView.layer.shadowColor = [UIColor blackColor].CGColor;
        _headerView.layer.shadowOpacity = .2;
        
        
        CGFloat contentWidth = 130;
        UIFont* titleFont = [UIFont stampedTitleLightFontWithSize:24];
        _titleView = [[UILabel alloc] initWithFrame:CGRectMake(xOffset, 36 - titleFont.leading + 8.5, contentWidth, titleFont.lineHeight)];
        _titleView.font = titleFont;
        _titleView.textColor = [UIColor stampedBlackColor];
        _titleView.lineBreakMode = UILineBreakModeTailTruncation;
        [_headerView addSubview:_titleView];
        
        UIFont* subtitleFont = [UIFont stampedFontWithSize:12];
        _subtitleView = [[UILabel alloc] initWithFrame:CGRectMake(xOffset, 50 - subtitleFont.leading + 5, contentWidth, subtitleFont.lineHeight)];
        _subtitleView.font = subtitleFont;
        _subtitleView.textColor = [UIColor stampedGrayColor];
        _subtitleView.backgroundColor = [UIColor clearColor];
        _subtitleView.lineBreakMode = UILineBreakModeTailTruncation;
        [_headerView addSubview:_subtitleView];
        
        CGFloat spacingConstant = 4;
        
        CGRect seekFrame = CGRectMake(0, 16, 28, 28);
        UIButton* seekBackButton = [UIButton buttonWithType:UIButtonTypeCustom];
        seekBackButton.frame = CGRectOffset(seekFrame, 170 + 2 * spacingConstant, 0);
        [seekBackButton setImage:[UIImage imageNamed:@"musicplayer-rwdbtn"] forState:UIControlStateNormal];
        [seekBackButton addTarget:self action:@selector(seekBack:) forControlEvents:UIControlEventTouchUpInside];
        [_headerView addSubview:seekBackButton];
        
        UIButton* seekForwardButton = [UIButton buttonWithType:UIButtonTypeCustom];
        seekForwardButton.frame = CGRectOffset(seekFrame, 255, 0);
        [seekForwardButton setImage:[UIImage imageNamed:@"musicplayer-ffwbtn"] forState:UIControlStateNormal];
        [seekForwardButton addTarget:self action:@selector(seekForward:) forControlEvents:UIControlEventTouchUpInside];
        [_headerView addSubview:seekForwardButton];
        
        _pauseButton = [[UIButton buttonWithType:UIButtonTypeCustom] retain];
        _pauseButton.frame = CGRectMake(206 + spacingConstant, 10.5, 40, 40);
        [_pauseButton setImage:[UIImage imageNamed:@"musicplayer-playbtn"] forState:UIControlStateNormal];
        [_pauseButton setImage:[UIImage imageNamed:@"musicplayer-pausebtn"] forState:UIControlStateSelected];
        [_pauseButton addTarget:self action:@selector(pauseButtonPressed:) forControlEvents:UIControlEventTouchUpInside];
        [_headerView addSubview:_pauseButton];
        
        STRippleBar* topBar = [[[STRippleBar alloc] initWithPrimaryColor:@"eaeaea" andSecondaryColor:@"eaeaea" isTop:YES] autorelease];
        topBar.frame = CGRectMake(0, 0, _headerView.frame.size.width, topBar.frame.size.height);
        topBar.clipsToBounds = YES;
        [_headerView addSubview:topBar];
        
        _imageView = [[UIImageView alloc] initWithFrame:CGRectMake(10, 10, 44, 44)];
        [_headerView addSubview:_imageView];
        
        _tableView = [[UITableView alloc] initWithFrame:CGRectMake(0, headerHeight, self.frame.size.width, self.frame.size.height - (headerHeight + (_fullFooter ? footerHeight : 0)))];
        _tableView.dataSource = self;
        _tableView.delegate = self;
        [self addSubview:_tableView];
        
        [self addSubview:_headerView];
        
        _footerView = [[UIView alloc] initWithFrame:CGRectMake(0, self.frame.size.height - footerHeight, self.frame.size.width, footerHeight)];
        
        STRippleBar* footerBar = [[[STRippleBar alloc] initWithPrimaryColor:@"eaeaea" andSecondaryColor:@"eaeaea" isTop:NO] autorelease];
        footerBar.frame = CGRectMake(0, _footerView.frame.size.height - footerBar.frame.size.height, _footerView.frame.size.width, footerBar.frame.size.height);
        footerBar.clipsToBounds = YES;
        [_footerView addSubview:footerBar];
        
        if (_fullFooter) {
            _editButton = [[UIButton buttonWithType:UIButtonTypeCustom] retain];
            [_editButton addTarget:self action:@selector(toggleEdit:) forControlEvents:UIControlEventTouchUpInside];
            [_editButton setImage:[UIImage imageNamed:@"menu_icon-settings"] forState:UIControlStateNormal];
            _editButton.frame = CGRectMake(10, 10, 30, 30);
            [_footerView addSubview:_editButton];
            _footerView.backgroundColor = [UIColor whiteColor];
            _footerView.layer.shadowOffset = CGSizeMake(0, -2);
            _footerView.layer.shadowOpacity = .2;
            _footerView.layer.shadowColor = [UIColor blackColor].CGColor;
        }
        else {
            _footerView.backgroundColor = [UIColor clearColor];
            [Util addGradientToLayer:_footerView.layer 
                          withColors:[NSArray arrayWithObjects:
                                      [UIColor colorWithWhite:1 alpha:.0],
                                      [UIColor colorWithWhite:1 alpha:1],
                                      nil]
                            vertical:YES];
        }
        [self addSubview:_footerView];
        
        
        UIButton* exitButton = [UIButton buttonWithType:UIButtonTypeCustom];
        [exitButton addTarget:self action:@selector(exit:) forControlEvents:UIControlEventTouchUpInside];
        [exitButton setImage:[UIImage imageNamed:@"popup_wht_closeButton"] forState:UIControlStateNormal];
        exitButton.frame = CGRectMake(-24, -24, 48, 48);
        [self addSubview:exitButton];
        [self.tableView reloadData];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(changed:) name:STPlayerItemChangedNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(changed:) name:STPlayerStateChangedNotification object:nil];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(changed:) name:STPlayerPlaylistChangedNotification object:nil];
        [self update];
    }
    return self;
}

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [_footerView release];
    [_editButton release];
    [_headerView release];
    [_tableView release];
    [_player release];
    [_pauseButton release];
    [super dealloc];
}

- (void)changed:(id)notImportant {
    [self update];
}

- (void)toggleEdit:(id)notImportant {
    self.tableView.editing = !self.tableView.editing;
}

- (void)seekBack:(id)notImportant {
    NSInteger next = self.player.currentItemIndex - 1;
    if (next == -1) {
        next = self.player.itemCount - 1;
    }
    [self.player seekToItemAtIndex:next];
}

- (void)seekForward:(id)notImportant {
    NSInteger next = self.player.currentItemIndex + 1;
    if (next >= self.player.itemCount) {
        next = 0;
    }
    [self.player seekToItemAtIndex:next];
}

- (void)pauseButtonPressed:(UIButton*)button {
    BOOL paused = button.selected;
    NSLog(@"pausing %d", paused);
    self.player.paused = button.selected;
}

- (void)exit:(id)notImportant {
    [Util setFullScreenPopUp:nil dismissible:YES withBackground:[UIColor clearColor]];
}

+ (void)present {
    STPlayerPopUp* popUp = [[[STPlayerPopUp alloc] init] autorelease];
    [Util setFullScreenPopUp:popUp dismissible:YES withBackground:[UIColor colorWithWhite:0 alpha:.5]];
}

+ (void)presentWithItems:(NSArray<STPlaylistItem>*)playlist clear:(BOOL)clear {
    STPlayer* player = [STPlayer sharedInstance];
    if (clear) {
        [player clear];
    }
    player.paused = YES;
    for (NSInteger i = 0; i < playlist.count; i++) {
        id<STPlaylistItem> item = [playlist objectAtIndex:i];
        [player addPlaylistItem:item atIndex:i];
    }
    if (player.itemCount > 0) {
        [player seekToItemAtIndex:0];
        player.paused = NO;
    }
    [self present];
}


- (void)update {
    [self.tableView reloadData];
    id<STPlaylistItem> item = [self.player itemAtIndex:self.player.currentItemIndex];   
    _titleView.text = item.name;
    _subtitleView.text = item.subtitle;
    id<STImage> bestImage = [Util bestImageFromImages:item.images forSize:_imageView.frame.size];
    if (bestImage) {
        void (^block)(UIImage* image) = ^(UIImage* image) {
            self.imageView.image = image;
        };
        NSString* url = bestImage.url;
        UIImage* cachedImage = [[STImageCache sharedInstance] cachedImageForImageURL:url];
        if (cachedImage) {
            block(cachedImage);
        }
        else {
            [[STImageCache sharedInstance] imageForImageURL:url andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                block(image); 
            }];
        }
    }
    else {
        self.imageView.image = [UIImage imageNamed:@"TEMP_noImage"];
    }
    _pauseButton.selected = !self.player.paused;
    [Util executeOnMainThread:^{
        self.selectMask = YES;
        [self.tableView selectRowAtIndexPath:[NSIndexPath indexPathForRow:self.player.currentItemIndex inSection:0] animated:YES scrollPosition:UITableViewScrollPositionNone];
        self.selectMask = NO;
    }];
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section {
    return self.player.itemCount;
}

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView {
    return 1;
}

- (BOOL)tableView:(UITableView *)tableview canMoveRowAtIndexPath:(NSIndexPath *)indexPath {
	return YES;	
}

- (void)tableView:(UITableView *)tableView moveRowAtIndexPath:(NSIndexPath *)fromIndexPath toIndexPath:(NSIndexPath *)toIndexPath {
    [self.player moveItemAtIndex:fromIndexPath.row toIndex:toIndexPath.row];
}

- (void)edit:(id)notImportant {
    self.tableView.editing = YES;
}

- (void)unedit:(id)notImportant {
    self.tableView.editing = YES;
}

- (UITableViewCell*)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    NSString* reuseID = @"PlayerCell";
    STPlayerPopUpCell* cell = [tableView dequeueReusableCellWithIdentifier:reuseID];
    if (!cell) {
        cell = [[[STPlayerPopUpCell alloc] initWithReuseIdentifier:reuseID] autorelease];
    }
    id<STPlaylistItem> item = [self.player itemAtIndex:indexPath.row];
    [cell setupWithPlaylistItem:item];
    return cell;
}


- (void)tableView:(UITableView*)tableView didSelectRowAtIndexPath:(NSIndexPath*)indexPath {
    if (!self.selectMask) {
        if (indexPath.row == self.player.currentItemIndex) {
            self.player.paused = !self.player.paused;
        }
        else {
            [self.player seekToItemAtIndex:indexPath.row];
            self.player.paused = NO;
        }
    }
}

- (BOOL)tableView:(UITableView*)tableView canEditRowAtIndexPath:(NSIndexPath *)indexPath {
    return NO;
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath {
    if (editingStyle == UITableViewCellEditingStyleDelete) {
        [self.player removeItemAtIndex:indexPath.row];
    }
}

@end


@implementation STPlayerPopUpCell

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier
{
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
    if (self) {
        self.shouldIndentWhileEditing = NO;
        self.showsReorderControl = YES;
        self.textLabel.font = [UIFont stampedBoldFontWithSize:14];
        self.textLabel.textColor = [UIColor stampedDarkGrayColor];
    }
    return self;
}

- (void)setupWithPlaylistItem:(id<STPlaylistItem>)item {
    self.textLabel.text = item.name;
}

@end
