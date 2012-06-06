//
//  FriendTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import "FriendTableCell.h"
#import "STAvatarView.h"
#import "FriendStatusButton.h"
#import "UserStampView.h"

@interface FriendTableCell ()
@end

@implementation FriendTableCell

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {

        STAvatarView *view = [[STAvatarView alloc] initWithFrame:CGRectMake(10.0f, 4.0f, 46.0f, 46.0f)];
        view.backgroundColor = [UIColor whiteColor];
        [self addSubview:view];
        [view release];
        _avatarView = view;
        
        view.backgroundView.layer.shadowRadius = 3.0f;
        view.backgroundView.layer.shadowOpacity = 0.3f;
        
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
        
        FriendStatusButton *button = [[FriendStatusButton alloc] initWithFrame:CGRectMake(self.bounds.size.width - 64.0f, 10.0f, 54.0f, 30.0f)];
        [button addTarget:self action:@selector(action:) forControlEvents:UIControlEventTouchUpInside];
        button.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin;
        button.backgroundColor = [UIColor whiteColor];
        [self addSubview:button];
        _actionButton = button;
        
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

}


#pragma mark - Setters

- (void)setupWithUser:(id<STUser>)user {
    
    [_avatarView setImageURL:[NSURL URLWithString:[user imageURL]]];
    _titleLabel.text = user.name;
    _detailTitleLabel.text = [NSString stringWithFormat:@"@%@", user.screenName];

    [_stampView setupWithUser:user];

    [_actionButton setLoading:NO];
    [_actionButton setStatus:FriendStatusNotFollowing];
    
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];
    [_stampView setNeedsDisplay];
}

- (void)setHighlighted:(BOOL)highlighted animated:(BOOL)animated {
    [super setHighlighted:highlighted animated:animated];
    [_stampView setNeedsDisplay];
}


#pragma mark - Actions

- (void)action:(id)sender {
    
    [_actionButton setLoading:YES];
    
    double delayInSeconds = 2.0;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        [_actionButton setLoading:NO];
        [_actionButton setStatus:FriendStatusFollowing];
    });

}

@end
