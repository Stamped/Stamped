//
//  CreditUserTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import "CreditUserTableCell.h"
#import "STAvatarView.h"
#import "UserStampView.h"

@implementation CreditUserTableCell
@synthesize checked=_checked;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
    
        STAvatarView *view = [[STAvatarView alloc] initWithFrame:CGRectMake(10.0f, 4.0f, 46.0f, 46.0f)];
        view.userInteractionEnabled = NO;
        view.backgroundColor = [UIColor whiteColor];
        [self addSubview:view];
        [view release];
        _avatarView = view;
        
        view.backgroundView.layer.shadowRadius = 1.0f;
        view.backgroundView.layer.shadowOpacity = 0.2f;
        
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
        
        UserStampView *stampView = [[UserStampView alloc] initWithFrame:CGRectMake(44.0f, 2.0f, 18.0f, 18.0f)];
        stampView.size = STStampImageSize18;
        [self addSubview:stampView];
        [stampView release];
        _stampView = stampView;
        
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"following_check_icon.png"]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin;
        [self addSubview:imageView];
        _checkView = imageView;
        
        CGRect frame = imageView.frame;
        frame.origin.x = (self.bounds.size.width - (frame.size.width+20.0f));
        frame.origin.y = (self.bounds.size.height - frame.size.height)/2;
        imageView.frame = frame;
        [imageView release];
        
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [_titleLabel sizeToFit];
    [_detailTitleLabel sizeToFit];
    
    CGRect frame = _titleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width -120.0f, frame.size.width);
    _titleLabel.frame = frame;
    
    frame = _detailTitleLabel.frame;
    frame.size.width = MIN(self.bounds.size.width -120.0f, frame.size.width);
    _detailTitleLabel.frame = frame;
    
}


#pragma mark - Setters

- (void)setupWithUser:(id<STUser>)user {
    
    [_avatarView setImageURL:[NSURL URLWithString:[user imageURL]]];
    _detailTitleLabel.text = user.name;
    _titleLabel.text = user.screenName;
    [_stampView setupWithUser:user];
        
}

- (void)setChecked:(BOOL)checked {
    _checked = checked;
    
    if (_checkView) {
        _checkView.image = [UIImage imageNamed:_checked ? @"following_check_icon_hi.png" : @"following_check_icon.png"];
    }
    
}

@end
