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
#import "STRdio.h"
#import "STSpotify.h"

static const CGFloat _cellHeight = 52;

@interface STPlayerPopUpCell : UITableViewCell

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier;
- (void)setupWithPlaylistItem:(id<STPlaylistItem>)item andIndex:(NSInteger)index;

@property (nonatomic, readonly, retain) UILabel* indexLabel;
@property (nonatomic, readonly, retain) UILabel* titleLabel;
@property (nonatomic, readonly, retain) UIImageView* playerIcon;
@property (nonatomic, readonly, retain) UILabel* lengthLabel;

@end

@interface STPlayerPopUp () <UITableViewDataSource, UITableViewDelegate>

@property (nonatomic, readonly, retain) UIView* contentView;
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
@property (nonatomic, readonly, retain) UILabel* viaLabel;

@end

@implementation STPlayerPopUp

@synthesize contentView = _contentView;
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
@synthesize viaLabel = _viaLabel;

- (id)init
{
    self = [super initWithFrame:[Util fullscreenFrame]];
    if (self) {
        self.backgroundColor = [UIColor clearColor];
        _contentView = [[UIView alloc] initWithFrame:CGRectMake(15, 55, 290, 360)];
        _contentView.backgroundColor = [UIColor whiteColor];
        
        _fullFooter = !([STRdio sharedRdio].connected || [STSpotify sharedInstance].connected);// YES;//![STRdio sharedRdio].loggedIn;
        
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
        _headerView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, _contentView.frame.size.width, headerHeight)];
        _headerView.backgroundColor = [UIColor whiteColor];
        //_headerView.clipsToBounds = YES;
        _headerView.layer.shadowOffset = CGSizeMake(0, 2);
        _headerView.layer.shadowColor = [UIColor blackColor].CGColor;
        _headerView.layer.shadowOpacity = .2;
        
        CGFloat viaWidth = 120;
        _viaLabel = [[UILabel alloc] initWithFrame:CGRectMake(_headerView.frame.size.width - viaWidth, 48, viaWidth, 18)];
        _viaLabel.font = [UIFont stampedFontWithSize:10];
        _viaLabel.textColor = [UIColor stampedGrayColor];
        _viaLabel.textAlignment = UITextAlignmentCenter;
        [_headerView addSubview:_viaLabel];
        
        CGFloat contentWidth = 110;
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
        
        _tableView = [[UITableView alloc] initWithFrame:CGRectMake(0, headerHeight, _contentView.frame.size.width, _contentView.frame.size.height - (headerHeight + (_fullFooter ? footerHeight : 0)))];
        _tableView.dataSource = self;
        _tableView.delegate = self;
        [_contentView addSubview:_tableView];
        
        [_contentView addSubview:_headerView];
        
        _footerView = [[UIView alloc] initWithFrame:CGRectMake(0, _contentView.frame.size.height - footerHeight, _contentView.frame.size.width, footerHeight)];
        
        STRippleBar* footerBar = [[[STRippleBar alloc] initWithPrimaryColor:@"eaeaea" andSecondaryColor:@"eaeaea" isTop:NO] autorelease];
        footerBar.frame = CGRectMake(0, _footerView.frame.size.height - footerBar.frame.size.height, _footerView.frame.size.width, footerBar.frame.size.height);
        footerBar.clipsToBounds = YES;
        [_footerView addSubview:footerBar];
        
        if (_fullFooter) {
            
            _footerView.backgroundColor = [UIColor whiteColor];
            _footerView.layer.shadowOffset = CGSizeMake(0, -2);
            _footerView.layer.shadowOpacity = .2;
            _footerView.layer.shadowColor = [UIColor blackColor].CGColor;
            
            //            _editButton = [[UIButton buttonWithType:UIButtonTypeCustom] retain];
            //            [_editButton addTarget:self action:@selector(toggleEdit:) forControlEvents:UIControlEventTouchUpInside];
            //            [_editButton setImage:[UIImage imageNamed:@"menu_icon-settings"] forState:UIControlStateNormal];
            //            _editButton.frame = CGRectMake(10, 10, 30, 30);
            //            [_footerView addSubview:_editButton];
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
        [_contentView addSubview:_footerView];
        
        
        UIButton* exitButton = [UIButton buttonWithType:UIButtonTypeCustom];
        [exitButton addTarget:self action:@selector(exit:) forControlEvents:UIControlEventTouchUpInside];
        [exitButton setImage:[UIImage imageNamed:@"popup_wht_closeButton"] forState:UIControlStateNormal];
        exitButton.frame = CGRectMake(-24 + _contentView.frame.origin.x, -24 + _contentView.frame.origin.y, 48, 48);
        [self addSubview:_contentView];
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
    [_contentView release];
    [super dealloc];
}

+ (UIColor*)backgroundColor {
    return [UIColor colorWithWhite:0 alpha:.5];
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
    self.player.paused = paused;
}

static CGFloat _time = .4;

- (void)exit:(id)notImportant {
    STPlayerService service = self.player.currentTrackService;
    if (service == STPlayerServicePreview) {
        self.player.paused = YES;
    }
    [UIView animateWithDuration:_time animations:^{
        self.backgroundColor = [UIColor clearColor];
    } completion:^(BOOL finished) {
        UIView* snapshot = [STPlayerPopUp snapshot:self];
        [STPlayerPopUp expand:snapshot withPopUp:self];
        [Util setFullScreenPopUp:snapshot dismissible:NO animated:NO withBackground:[UIColor clearColor]];
        [UIView animateWithDuration:_time animations:^{
            [STPlayerPopUp collapse:snapshot withPopUp:self];
        } completion:^(BOOL finished) {
            [Util setFullScreenPopUp:nil dismissible:YES animated:NO withBackground:[UIColor clearColor]]; 
        }];
    }];
}

+ (CGRect)collapseFrame {
    return CGRectMake(220, 15, 0, 0);
}

+ (UIView*)snapshot:(STPlayerPopUp*)popUp {
    UIGraphicsBeginImageContext(popUp.frame.size);
    [popUp.layer renderInContext:UIGraphicsGetCurrentContext()];
    CGContextRef context = UIGraphicsGetCurrentContext();
    CGContextTranslateCTM(context, popUp.frame.origin.x, popUp.frame.origin.y);
    UIImage *resultingImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    UIImageView* imageView = [[[UIImageView alloc] initWithImage:resultingImage] autorelease];
    return imageView;
}

+ (void)collapse:(UIView*)view withPopUp:(STPlayerPopUp*)popUp{
    view.frame = [self collapseFrame];
    view.alpha = 0;
}

+ (void)expand:(UIView*)view  withPopUp:(STPlayerPopUp*)popUp{
    view.frame = popUp.frame;
    view.alpha = 1;
}

+ (void)present {
    STPlayerPopUp* popUp = [[[STPlayerPopUp alloc] init] autorelease];
    UIView* snapshot = [self snapshot:popUp];
    [self collapse:snapshot withPopUp:popUp];
    [Util setFullScreenPopUp:snapshot dismissible:NO animated:NO withBackground:[UIColor clearColor]];
    [UIView animateWithDuration:_time delay:0 options:UIViewAnimationCurveEaseInOut animations:^{
        [self expand:snapshot withPopUp:popUp];
            
    } completion:^(BOOL finished) {
        [Util setFullScreenPopUp:popUp dismissible:YES animated:NO withBackground:[UIColor clearColor]]; 
        [UIView animateWithDuration:_time animations:^{
            popUp.backgroundColor = [self backgroundColor]; 
        }];
        
    }];
}

+ (void)presentWithItems:(NSArray<STPlaylistItem>*)playlist clear:(BOOL)clear startIndex:(NSInteger)index {
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
        [player seekToItemAtIndex:index];
        player.paused = NO;
    }
    [self present];
}


- (void)update {
    [self.tableView reloadData];
    if (self.player.itemCount) {
        id<STPlaylistItem> item = [self.player itemAtIndex:self.player.currentItemIndex];   
        if (item) {
            _titleView.text = item.name;
            _subtitleView.text = item.subtitle;
            STPlayerService service = self.player.currentTrackService;
            NSString* serviceString = nil;
            if (service == STPlayerServicePreview) {
                serviceString = @"iTunes";
            }
            else if (service == STPlayerServiceRdio) {
                serviceString = @"Rdio";
            }
            else if (service == STPlayerServiceSpotify) {
                serviceString = @"Spotify";
            }
            if (serviceString) {
                _viaLabel.text = [NSString stringWithFormat:@"via %@", serviceString];
            }
            else {
                _viaLabel.text = @"";
            }
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
    }
}

- (CGFloat)tableView:(UITableView *)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    return _cellHeight;
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
    [cell setupWithPlaylistItem:item andIndex:indexPath.row];
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

@synthesize indexLabel = _indexLabel;
@synthesize titleLabel = _titleLabel;
@synthesize playerIcon = _playerIcon;
@synthesize lengthLabel = _lengthLabel;

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier
{
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
    if (self) {
        self.shouldIndentWhileEditing = NO;
        self.showsReorderControl = YES;
        self.textLabel.font = [UIFont stampedBoldFontWithSize:12];
        self.textLabel.textColor = [UIColor stampedDarkGrayColor];
        
        _titleLabel = [[UILabel alloc] initWithFrame:CGRectMake(60, 0, 185, 52)];
        _titleLabel.backgroundColor = [UIColor clearColor];
        _titleLabel.font = [UIFont stampedBoldFontWithSize:12];
        _titleLabel.textColor = [UIColor stampedDarkGrayColor];
        _titleLabel.highlightedTextColor = [UIColor whiteColor];
        
        [self.contentView addSubview:_titleLabel];
        
        _indexLabel = [[UILabel alloc] initWithFrame:CGRectMake(42, .5, 35, 52)];
        _indexLabel.backgroundColor = [UIColor clearColor];
        _indexLabel.font = [UIFont stampedFontWithSize:12];
        _indexLabel.textColor = [UIColor stampedGrayColor];
        _indexLabel.highlightedTextColor = [UIColor whiteColor];
        [self.contentView addSubview:_indexLabel];
        
        CGFloat rightSide = 275;
        CGFloat lengthWidth = 27;
        _lengthLabel = [[UILabel alloc] initWithFrame:CGRectMake(rightSide - lengthWidth, .5, lengthWidth, _cellHeight)];
        _lengthLabel.backgroundColor = [UIColor clearColor];
        _lengthLabel.font = [UIFont stampedFontWithSize:12];
        _lengthLabel.textColor = [UIColor stampedGrayColor];
        _lengthLabel.highlightedTextColor = [UIColor whiteColor];
        _lengthLabel.textAlignment = UITextAlignmentRight;
        [self.contentView addSubview:_lengthLabel];
    }
    return self;
}

- (void)setupWithPlaylistItem:(id<STPlaylistItem>)item andIndex:(NSInteger)index {
    _titleLabel.text = item.name;
    _lengthLabel.text = @"";
    if (item.length > 0) {
        _lengthLabel.text = [Util trackLengthString:item.length];
    }
    _indexLabel.text = [NSString stringWithFormat:@"%d.", index + 1];
    _playerIcon.image = nil;
}

@end
