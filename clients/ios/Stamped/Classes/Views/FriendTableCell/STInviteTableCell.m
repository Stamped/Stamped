//
//  STInviteTableCell.m
//  Stamped
//
//  Created by Landon Judkins on 7/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInviteTableCell.h"
#import "STAvatarView.h"
#import "UIButton+Stamped.h"
#import "STImageCache.h"

@interface STInviteTableCell  ()

@property (nonatomic, readonly, retain) UIImageView* userImageView;
@property (nonatomic, readonly, retain) UILabel* titleLabel;
@property (nonatomic, readonly, retain) UILabel* detailTitleLabel;
@property (nonatomic, readonly, retain) UIButton* inviteButton;
@property (nonatomic, readwrite, retain) STContact* contact;
@property (nonatomic, readwrite, retain) STCancellation* imageCancellation;

@end

@implementation STInviteTableCell

@synthesize userImageView = _userImageView;
@synthesize titleLabel = _titleLabel;
@synthesize detailTitleLabel = _detailTitleLabel;
@synthesize inviteButton = inviteButton_;
@synthesize contact = _contact;
@synthesize delegate = _delegate;
@synthesize imageCancellation = _imageCancellation;

- (id)initWithReuseIdentifier:(NSString *)reuseIdentifier
{
    self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier];
    if (self) {
        // Initialization code
        _userImageView = [[UIImageView alloc] initWithFrame:CGRectMake(10.0f, 4.0f, 46.0f, 46.0f)];
        _userImageView.userInteractionEnabled = NO;
        _userImageView.backgroundColor = [UIColor whiteColor];
        [self.contentView addSubview:_userImageView];
        
        _userImageView.layer.shadowRadius = 1.0f;
        _userImageView.layer.shadowOpacity = 0.2f;
        _userImageView.layer.shadowOffset = CGSizeMake(0, 1);
        _userImageView.layer.borderWidth = 2;
        _userImageView.layer.borderColor = [UIColor whiteColor].CGColor;
        
        _titleLabel = [[UILabel alloc] initWithFrame:CGRectMake(70.0f, 10.0f, 0.0f, 0.0f)];
        _titleLabel.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        _titleLabel.font = [UIFont boldSystemFontOfSize:16];
        _titleLabel.backgroundColor = [UIColor whiteColor];
        _titleLabel.textColor = [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f];
        _titleLabel.highlightedTextColor = [UIColor whiteColor];
        [self.contentView addSubview:_titleLabel];
        
        _detailTitleLabel = [[UILabel alloc] initWithFrame:CGRectMake(70.0f, 30.0f, 0.0f, 0.0f)];
        _detailTitleLabel.autoresizingMask = UIViewAutoresizingFlexibleBottomMargin;
        _detailTitleLabel.font = [UIFont systemFontOfSize:12];
        _detailTitleLabel.backgroundColor = [UIColor whiteColor];
        _detailTitleLabel.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        _detailTitleLabel.highlightedTextColor = [UIColor whiteColor];
        [self.contentView addSubview:_detailTitleLabel];
        
        
        inviteButton_ = [[UIButton stampedWhiteButton] retain];
        [inviteButton_ setTitle:@"Invite" forState:UIControlStateNormal];
        [inviteButton_ setTitleColor:[UIColor colorWithRed:0.2 green:0.45 blue:0.8 alpha:1.0]
                            forState:UIControlStateNormal];
        
        [inviteButton_ setTitle:@"" forState:UIControlStateSelected];
        [inviteButton_ setImage:[UIImage imageNamed:@"buttonImg_check"] forState:UIControlStateSelected];
        
        [inviteButton_ setTitle:@"Invited" forState:UIControlStateDisabled];
        
        [inviteButton_ sizeToFit];
        [inviteButton_ addTarget:self action:@selector(inviteButtonPressed:) forControlEvents:UIControlEventTouchUpInside];
        CGFloat width = CGRectGetWidth(inviteButton_.frame) + 25;
        inviteButton_.frame = CGRectMake(320 - width - 5, 10, width, 29);
        [self.contentView addSubview:inviteButton_];
        self.selectionStyle = UITableViewCellSelectionStyleNone;
    }
    return self;
}

- (void)dealloc
{
    [self releaseContact];
    [_userImageView release];
    [_titleLabel release];
    [_detailTitleLabel release];
    [inviteButton_ release];
    [super dealloc];
}

- (void)releaseContact {
    if (self.contact) {
        [self.contact removeObserver:self forKeyPath:@"invite"];
    }
    self.contact = nil;
    [self.imageCancellation cancel];
    self.imageCancellation = nil;
}

- (void)setupWithContact:(STContact*)contact {
    [self releaseContact];
    self.contact = contact;
    [contact addObserver:self forKeyPath:@"invite" options:0 context:nil];
    self.inviteButton.selected = contact.invite;
    _userImageView.image = nil;
    if (contact.image) {
        _userImageView.image = contact.image;
    }
    else if (contact.imageURL) {
        UIImage* fastImage = [[STImageCache sharedInstance] cachedImageForImageURL:contact.imageURL];
        if (fastImage) {
            _userImageView.image = fastImage;
        }
        else {
            self.imageCancellation = [[STImageCache sharedInstance] imageForImageURL:contact.imageURL andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                if ([self.contact.imageURL isEqualToString:contact.imageURL]) {
                    _userImageView.image = image; 
                }
            }];
        }
    }
    if (!_userImageView.image) {
        _userImageView.image = [UIImage imageNamed:@"default_user_image"];
    }
    _titleLabel.text = contact.name;
    [_titleLabel sizeToFit];
    CGRect titleFrame = _titleLabel.frame;
    titleFrame.size.width = MIN(titleFrame.size.width, 180);
    _titleLabel.frame = titleFrame;
    _detailTitleLabel.hidden = YES;
    if (contact.emailAddresses.count) {
        _detailTitleLabel.text = [contact.emailAddresses objectAtIndex:0];
        _detailTitleLabel.hidden = NO;
        [_detailTitleLabel sizeToFit];
        CGRect frame = _detailTitleLabel.frame;
        frame.size.width = MIN(frame.size.width, 180);
        _detailTitleLabel.frame = frame;
    }
    
    [self updateButton];
}

- (void)updateButton {
    self.inviteButton.selected = self.contact.invite;
}

- (void)inviteButtonPressed:(id)sender {
    [self.delegate inviteTableCellToggleInvite:self];
}

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context {
    if (object == self.contact && [keyPath isEqualToString:@"invite"]) {
        [self updateButton];
    }
    else {
        [super observeValueForKeyPath:keyPath ofObject:object change:change context:context];
    }
}

@end
