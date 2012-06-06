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

@interface UserHeaderTabView : UIView
@property(nonatomic,assign) id delegate;
- (void)setSelectedTab:(STUserHeaderTab)tab;
@end

@implementation STUserHeaderView
@synthesize selectedTab=_selectedTab;
@synthesize delegate;
@synthesize showStats;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.clipsToBounds = YES;
        
        STAvatarView *view = [[STAvatarView alloc] initWithFrame:CGRectMake(10.0f, 10.0f, 76.0f, 76.0f)];
        view.backgroundColor = [UIColor whiteColor];
        [self addSubview:view];
        [view release];
        _avatarView = view;
        
        view.imageView.frame = CGRectInset(view.imageView.frame, 1, 1);
        view.backgroundView.layer.shadowRadius = 2.0f;
        view.backgroundView.layer.shadowOpacity = 0.25f;
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(70.0f, 10.0f, 0.0f, 0.0f)];
        label.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        label.font = [UIFont boldSystemFontOfSize:16];
        label.backgroundColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        [self addSubview:label];
        [label release];
        _titleLabel = label;
        
        label = [[UILabel alloc] initWithFrame:CGRectMake(70.0f, 30.0f, 0.0f, 0.0f)];
        label.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        label.font = [UIFont systemFontOfSize:12];
        label.backgroundColor = [UIColor whiteColor];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        label.highlightedTextColor = [UIColor whiteColor];
        [self addSubview:label];
        [label release];
        _detailTitleLabel = label;
        
        UserStampView *stampView = [[UserStampView alloc] initWithFrame:CGRectMake(CGRectGetMaxX(_avatarView.frame) - 34, CGRectGetMinY(_avatarView.frame) - 34.0f, 60.0f, 60.0f)];
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
        
        self.selectedTab = STUserHeaderTabStamps;
        
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
}


#pragma mark - Setters

- (void)setupWithUser:(id<STUser>)user {
    
    [_avatarView setImageURL:[NSURL URLWithString:[user imageURL]]];
    _titleLabel.text = user.name;
    _detailTitleLabel.text = [NSString stringWithFormat:@"@%@", user.screenName];
    [_stampView setupWithUser:user];
    
}

- (void)setSelectedTab:(STUserHeaderTab)selectedTab {
    _selectedTab = selectedTab;
    
    [_tabView setSelectedTab:_selectedTab];
    
}


#pragma mark - Actions

- (void)tabHit:(UIButton*)sender {
    
    self.selectedTab = sender.tag;
    if ([(id)delegate respondsToSelector:@selector(stUserHeaderView:selectedTab:)]) {
        [self.delegate stUserHeaderView:self selectedTab:sender.tag];
    }
    
}


@end


#pragma mark - UserHeaderTabView 

@implementation UserHeaderTabView

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        CGRect frame = CGRectMake(0.0f, floorf(((self.bounds.size.height-44.0f)/2) + 4.0f), 44.0f, 44.0f);
        
        frame.origin.x = 80.0f;
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
        
        frame.origin.x = self.bounds.size.width - (80.0f + 44.0f);
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
