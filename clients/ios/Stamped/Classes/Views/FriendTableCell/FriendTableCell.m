//
//  FriendTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import "FriendTableCell.h"
#import "STAvatarView.h"

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
        
        STBlockUIView *stampView = [[STBlockUIView alloc] initWithFrame:CGRectMake(44.0f, 2.0f, 18.0f, 18.0f)];
        stampView.backgroundColor = [UIColor clearColor];
        [self addSubview:stampView];
        [stampView setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
          
            if (!_primaryColor || !_secondaryColor) return;
            
            CGContextSaveGState(ctx);
            CGContextTranslateCTM(ctx, 0.0f, rect.size.height);
            CGContextScaleCTM(ctx, 1.0f, -1.0f);
            CGContextClipToMask(ctx, rect, [UIImage imageNamed:@"stamp_18pt_texture.png"].CGImage);
            
            if (self.highlighted || self.selected) {
                
                [[UIColor whiteColor] setFill];
                CGContextFillRect(ctx, rect);
                
            } else {
                
                if (_primaryColor && _secondaryColor) {
                    drawStampGradient([_primaryColor CGColor], [_secondaryColor CGColor], ctx);
                } else {
                    CGContextFillRect(ctx, rect);
                }
                
            }
            
            CGContextRestoreGState(ctx);

            
        }];
        [stampView release];
        _stampView = stampView;
        
        UIImage *image = [UIImage imageNamed:@"nav_button_green.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.backgroundColor = [UIColor whiteColor];
        [button.titleLabel setFont:[UIFont boldSystemFontOfSize:12]];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        [button setTitleColor:[UIColor whiteColor] forState:UIControlStateNormal];
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:0.2f] forState:UIControlStateNormal];
        [button setTitle:@"Follow" forState:UIControlStateNormal];
        button.frame = CGRectMake(self.bounds.size.width - 70.0f, 10.0f, 60.0f, image.size.height);
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:5 topCapHeight:0.0f] forState:UIControlStateNormal];
        [button setBackgroundImage:[[UIImage imageNamed:@"nav_button_green_hi.png"] stretchableImageWithLeftCapWidth:5 topCapHeight:0.0f] forState:UIControlStateHighlighted];
        [self addSubview:button];
        _actionButton = button;
        
    }
    return self;
}

- (void)dealloc {
    [_primaryColor release], _primaryColor=nil;
    [_secondaryColor release], _secondaryColor=nil;
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

    float r,g,b;
    [Util splitHexString:user.primaryColor toRed:&r green:&g blue:&b];
    [_primaryColor release], _primaryColor=nil;
    _primaryColor = [[UIColor colorWithRed:r green:g blue:b alpha:1.0f] retain];
    [Util splitHexString:user.secondaryColor toRed:&r green:&g blue:&b];
    [_secondaryColor release], _secondaryColor=nil;
    _secondaryColor = [[UIColor colorWithRed:r green:g blue:b alpha:1.0f] retain];

    [_stampView setNeedsDisplay];
    
    
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
    
}

@end
