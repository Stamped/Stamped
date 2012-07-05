//
//  STUserHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 6/5/12.
//
//

#import "STUserHeaderView.h"
#import "STAvatarView.h"
#import "UserStampView.h"
#import "STSimpleUserDetail.h"
#import "STUserStatsView.h"
#import "STUserImageView.h"
#import "STStampedActions.h"
#import "Util.h"

@interface UserHeaderTabView : UIView
@property(nonatomic,assign) id delegate;
- (void)setSelectedTab:(STUserHeaderTab)tab;
@end

@interface STUserHeaderView ()

@property (nonatomic, readonly, retain) STUserImageView* userImageView;

@end

@implementation STUserHeaderView
@synthesize userImageView = _userImageView;
@synthesize selectedTab=_selectedTab;
@synthesize showingStats=_showingStats;
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.clipsToBounds = YES;
        _userImageView = [[STUserImageView alloc] initWithSize:76];
        [Util reframeView:_userImageView withDeltas:CGRectMake(10, 10, 0, 0)];
        [self addSubview:_userImageView];
        
//        STAvatarView *view = [[STAvatarView alloc] initWithFrame:CGRectMake(10.0f, 10.0f, 76.0f, 76.0f)];
//        view.delegate = (id<STAvatarViewDelegate>)self;
//        view.backgroundColor = [UIColor whiteColor];
//        [self addSubview:view];
//        [view release];
//        _avatarView = view;
//        [view setDefault];
//                
//        view.imageView.frame = CGRectInset(view.imageView.frame, 1, 1);
//        view.backgroundView.layer.shadowRadius = 1.0f;
//        view.backgroundView.layer.shadowOpacity = 0.2f;
//        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(108.0f, 30.0f, 0.0f, 0.0f)];
        label.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        label.font = [UIFont boldSystemFontOfSize:16];
        label.backgroundColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.shadowColor = [UIColor whiteColor];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        [self addSubview:label];
        [label release];
        _titleLabel = label;
        
        label = [[UILabel alloc] initWithFrame:CGRectMake(108.0f, CGRectGetMaxY(_titleLabel.frame) + 20.0f, 0.0f, 0.0f)];
        label.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        label.font = [UIFont systemFontOfSize:12];
        label.backgroundColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        label.shadowColor = [UIColor whiteColor];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        [self addSubview:label];
        [label release];
        _detailTitleLabel = label;
        
        UserStampView *stampView = [[UserStampView alloc] initWithFrame:CGRectMake(CGRectGetMaxX(_userImageView.frame) - 34, CGRectGetMinY(_userImageView.frame) - 34.0f, 60.0f, 60.0f)];
        stampView.size = STStampImageSize60;
        [self addSubview:stampView];
        [stampView release];
        _stampView = stampView;
        
        UIImage *image = [UIImage imageNamed:@"user_header_wave.png"];
        UserHeaderTabView *waveView = [[UserHeaderTabView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height-image.size.height, self.bounds.size.width, image.size.height)];
        waveView.delegate = self;
        waveView.backgroundColor = [UIColor colorWithPatternImage:image];
        waveView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleWidth;
        [self addSubview:waveView];
        [waveView release];
        _tabView = waveView;
        
    }
    return self;
}

- (void)dealloc {
    [_userImageView release];
    [super dealloc];
}

- (void)layoutSubviews {
    [_titleLabel sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.size.width = floorf(MIN(frame.size.width, self.bounds.size.width - (frame.origin.x+10.0f)));
    _titleLabel.frame = frame;
    
    [_detailTitleLabel sizeToFit];
    frame = _detailTitleLabel.frame;
    frame.size.width = floorf(MIN(frame.size.width, self.bounds.size.width - (frame.origin.x+10.0f)));
    _detailTitleLabel.frame = frame;
    
    [super layoutSubviews];
}


#pragma mark - Height

+ (CGFloat)heightWithStats:(BOOL)stats {
    
    return stats ? 235.0f : 155.0f;
    
}


#pragma mark - Setters

- (void)setupWithUser:(STSimpleUserDetail*)user {
    [_userImageView setupWithUser:user viewAction:NO];
    _titleLabel.text = user.name;
    if ([user respondsToSelector:@selector(location)] && [user location]) {
        _detailTitleLabel.text = [user location];
    } else {
        _detailTitleLabel.text = [NSString stringWithFormat:@"@%@", user.screenName];
    }
    [_stampView setupWithUser:user];
    
    if (_statsView) {
        [_statsView setupWithUser:user];
    }
    [_userImageView clearAction];
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewUserImage:user withOutputContext:context];
    [_userImageView setAction:action withContext:context];
    [self setNeedsLayout];
    
}

- (void)setSelectedTab:(STUserHeaderTab)selectedTab {
    _selectedTab = selectedTab;
    [_tabView setSelectedTab:_selectedTab];
    [self setShowingStats:(selectedTab == STUserHeaderTabStamps)];
}

- (void)setShowingStats:(BOOL)showingStats {
    _showingStats = showingStats;
    
    if (_showingStats) {
        
        if (!_statsView) {
            
            STUserStatsView *view = [[STUserStatsView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height - 80.0f, self.bounds.size.width, 80.0f)];
            view.delegate = (id<STUserStatsViewDelegate>)self;
            view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin;
            [self addSubview:view];
            [view release];
            _statsView = view;
            
        }
        
        _statsView.hidden = NO;
        
    } else {
        
        if (_statsView) {
            _statsView.hidden = YES;
        }
        
    }
    
    CGRect frame = self.frame;
    frame.size.height = [[self class] heightWithStats:_showingStats];
    self.frame = frame;
    
    frame = _tabView.frame;
    frame.origin.y = _showingStats ? self.bounds.size.height - (_tabView.bounds.size.height+80.0f) : self.bounds.size.height-_tabView.bounds.size.height;
    _tabView.frame = frame;
    
}


#pragma mark - Actions

- (void)tabHit:(UIButton*)sender {
    
    self.selectedTab = sender.tag;
    if ([(id)delegate respondsToSelector:@selector(stUserHeaderView:selectedTab:)]) {
        [self.delegate stUserHeaderView:self selectedTab:self.selectedTab];
    }
    
}


#pragma mark - STAvatarViewDelegate

- (void)stAvatarViewTapped:(STAvatarView*)view {
    
    if ([(id)delegate respondsToSelector:@selector(stUserHeaderViewAvatarTapped:)]) {
        [self.delegate stUserHeaderViewAvatarTapped:self];
    }
}


#pragma mark - STUserStatsViewDelegate

- (void)stUserStatsView:(STUserStatsView*)view didSelectStat:(STUserHeaderStat)stat {
    
    if ([(id)delegate respondsToSelector:@selector(stUserHeaderView:selectedStat:)]) {
        [self.delegate stUserHeaderView:self selectedStat:stat];
    }
    
}

@end


#pragma mark - UserHeaderTabView 

@implementation UserHeaderTabView

@synthesize delegate = _delegate;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        CGRect frame = CGRectMake(0.0f, floorf(((self.bounds.size.height-44.0f)/2) + 4.0f), 44.0f, 44.0f);
        
        frame.origin.x = 76.0f;
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.tag = STUserHeaderTabStamps;
        button.frame = frame;
        button.autoresizingMask = UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [button setImage:[UIImage imageNamed:@"user_header_stamp_icon.png"] forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"user_header_stamp_icon_hi.png"] forState:UIControlStateSelected];
        [self addSubview:button];
        
        frame.origin.x = (self.bounds.size.width-44.0f)/2;
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.tag = STUserHeaderTabGraph;
        button.frame = frame;
        button.autoresizingMask = UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [button setImage:[UIImage imageNamed:@"user_header_graph_icon.png"] forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"user_header_graph_icon_hi.png"] forState:UIControlStateSelected];
        [self addSubview:button];
        
        frame.origin.x = self.bounds.size.width - (76.0f + 44.0f);
        button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.tag = STUserHeaderTabInfo;
        button.frame = frame;
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [button setImage:[UIImage imageNamed:@"user_header_info_icon.png"] forState:UIControlStateNormal];
        [button setImage:[UIImage imageNamed:@"user_header_info_icon_hi.png"] forState:UIControlStateSelected];
        [self addSubview:button];

    }
    return self;
    
}

- (void)setSelectedTab:(STUserHeaderTab)tab {
    
    for (UIButton *button in self.subviews) {
        if ([button respondsToSelector:@selector(setSelected:)]) {
            button.selected = button.tag==tab;
        }
    }
    
}

- (void)buttonHit:(UIButton*)sender {
    
    [self.delegate tabHit:sender];
    
}

@end
